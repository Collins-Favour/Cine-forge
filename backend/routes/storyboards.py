"""
Storyboard Management Routes
Handles storyboard panel CRUD and AI image generation
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, StoryboardPanel, Scene, VisualStyle, Project
from utils.decorators import validate_request, project_permission_required
from utils.helpers import log_activity
from services import GeminiService
import time

storyboards_bp = Blueprint('storyboards', __name__)


@storyboards_bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def get_project_storyboards(project_id):
    """Get all storyboard panels for a project"""
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Get all scenes for the project
    scenes = Scene.query.filter_by(project_id=project_id).all()
    scene_ids = [s.scene_id for s in scenes]
    
    # Get all panels for these scenes
    panels = StoryboardPanel.query.filter(StoryboardPanel.scene_id.in_(scene_ids))\
        .order_by(StoryboardPanel.scene_id, StoryboardPanel.panel_number).all()
    
    return jsonify({
        'panels': [p.to_dict() for p in panels],
        'total': len(panels)
    }), 200


@storyboards_bp.route('/scene/<int:scene_id>/panels', methods=['GET'])
@jwt_required()
def get_panels(scene_id):
    """Get all storyboard panels for a scene"""
    scene = Scene.query.get(scene_id)
    if not scene:
        return jsonify({'error': 'Scene not found'}), 404
    
    panels = StoryboardPanel.query.filter_by(scene_id=scene_id)\
        .order_by(StoryboardPanel.panel_number).all()
    
    return jsonify({'panels': [p.to_dict() for p in panels]}), 200


@storyboards_bp.route('/scene/<int:scene_id>/panels', methods=['POST'])
@jwt_required()
@validate_request(['image_prompt'])
def create_panel(scene_id):
    """Create new storyboard panel"""
    user_id = get_jwt_identity()
    scene = Scene.query.get(scene_id)
    if not scene:
        return jsonify({'error': 'Scene not found'}), 404
    
    data = request.get_json()
    
    # Check panel limit
    from models import SystemSetting
    max_panels = SystemSetting.query.filter_by(setting_key='max_panels_per_scene').first()
    if max_panels:
        panel_count = StoryboardPanel.query.filter_by(scene_id=scene_id).count()
        if panel_count >= max_panels.get_value():
            return jsonify({'error': 'Maximum panels per scene reached'}), 403
    
    # Get next panel number
    last_panel = StoryboardPanel.query.filter_by(scene_id=scene_id)\
        .order_by(StoryboardPanel.panel_number.desc()).first()
    next_number = 1 if not last_panel else last_panel.panel_number + 1
    
    panel = StoryboardPanel(
        scene_id=scene_id,
        panel_number=next_number,
        image_prompt=data['image_prompt'],
        negative_prompt=data.get('negative_prompt'),
        style_reference=data.get('style_reference', 'cinematic'),
        camera_angle=data.get('camera_angle'),
        shot_type=data.get('shot_type', 'medium'),
        movement=data.get('movement'),
        notes=data.get('notes'),
        status='pending'
    )
    
    db.session.add(panel)
    log_activity(scene.project_id, user_id, 'panel_created', 
                f'Created storyboard panel {next_number} for scene {scene.scene_number}',
                'storyboard_panel', panel.panel_id)
    db.session.commit()
    
    return jsonify({
        'message': 'Storyboard panel created',
        'panel': panel.to_dict()
    }), 201


@storyboards_bp.route('/panels/<int:panel_id>', methods=['PUT'])
@jwt_required()
def update_panel(panel_id):
    """Update storyboard panel"""
    user_id = get_jwt_identity()
    panel = StoryboardPanel.query.get(panel_id)
    
    if not panel:
        return jsonify({'error': 'Panel not found'}), 404
    
    data = request.get_json()
    
    updatable_fields = ['image_prompt', 'negative_prompt', 'style_reference', 
                       'camera_angle', 'shot_type', 'movement', 'notes', 
                       'manual_image_url', 'is_approved']
    
    for field in updatable_fields:
        if field in data:
            setattr(panel, field, data[field])
    
    scene = Scene.query.get(panel.scene_id)
    log_activity(scene.project_id, user_id, 'panel_updated', 
                f'Updated storyboard panel {panel.panel_number}')
    db.session.commit()
    
    return jsonify({
        'message': 'Panel updated successfully',
        'panel': panel.to_dict()
    }), 200


@storyboards_bp.route('/panels/<int:panel_id>', methods=['DELETE'])
@jwt_required()
def delete_panel(panel_id):
    """Delete storyboard panel"""
    user_id = get_jwt_identity()
    panel = StoryboardPanel.query.get(panel_id)
    
    if not panel:
        return jsonify({'error': 'Panel not found'}), 404
    
    scene = Scene.query.get(panel.scene_id)
    panel_number = panel.panel_number
    
    db.session.delete(panel)
    log_activity(scene.project_id, user_id, 'panel_deleted', 
                f'Deleted storyboard panel {panel_number}')
    db.session.commit()
    
    return jsonify({'message': 'Panel deleted successfully'}), 200


@storyboards_bp.route('/panels/<int:panel_id>/generate', methods=['POST'])
@jwt_required()
def generate_panel_image(panel_id):
    """Generate AI image for storyboard panel"""
    user_id = get_jwt_identity()
    
    print(f"🎬 Received image generation request for panel_id: {panel_id}")
    
    panel = StoryboardPanel.query.get(panel_id)
    
    if not panel:
        print(f"❌ Panel {panel_id} not found in database")
        # Show all panels for debugging
        all_panels = StoryboardPanel.query.all()
        print(f"Available panels: {[p.panel_id for p in all_panels]}")
        return jsonify({'error': 'Panel not found'}), 404
    
    print(f"✅ Panel found: {panel.panel_id}")
    print(f"   Scene ID: {panel.scene_id}")
    print(f"   Image prompt: {panel.image_prompt[:100] if panel.image_prompt else 'None'}...")
    
    scene = Scene.query.get(panel.scene_id)
    
    if not scene:
        print(f"❌ Scene {panel.scene_id} not found")
        return jsonify({'error': 'Scene not found'}), 404
    
    try:
        gemini_service = GeminiService()
        
        # Get project visual style
        visual_style = VisualStyle.query.filter_by(
            project_id=scene.project_id,
            is_primary=True
        ).first()
        
        # Enhance prompt with project style
        enhanced_prompt = panel.image_prompt
        if visual_style:
            style_dict = {
                'mood_keywords': visual_style.mood_keywords,
                'color_palette': visual_style.color_palette
            }
            enhanced_prompt = gemini_service.enhance_prompt_for_consistency(
                panel.image_prompt, 
                style_dict
            )
        
        # Update panel status
        panel.status = 'generating'
        panel.generation_settings = {
            'enhanced_prompt': enhanced_prompt,
            'style_reference': panel.style_reference
        }
        db.session.commit()
        
        # Generate actual image using Gemini Imagen 3
        print(f"🎨 Generating image for panel {panel_id} with Gemini Imagen 3...")
        image_data = gemini_service.generate_image(
            prompt=enhanced_prompt,
            negative_prompt=panel.negative_prompt or "blurry, bad quality, distorted, text, watermark, low resolution"
        )
        
        if image_data:
            # Save image to database as base64
            panel.generated_image_url = image_data
            panel.status = 'completed'
            panel.generation_timestamp = db.func.now()
            panel.ai_model_used = 'Pollinations.ai'
            
            print(f"✅ Image generated successfully for panel {panel_id}")
        else:
            panel.status = 'failed'
            db.session.commit()
            return jsonify({'error': 'Image generation failed. Please try again.'}), 500
        
        # Log AI processing
        from models import AIProcessingLog
        ai_log = AIProcessingLog(
            project_id=scene.project_id,
            user_id=user_id,
            operation_type='image_generation',
            input_data={'panel_id': panel_id, 'prompt': enhanced_prompt},
            output_data={'status': 'completed', 'has_image': bool(image_data)},
            ai_model='Gemini Imagen 3',
            status='completed'
        )
        db.session.add(ai_log)
        
        log_activity(scene.project_id, user_id, 'panel_generated', 
                    f'Generated image for panel {panel.panel_number}')
        db.session.commit()
        
        return jsonify({
            'message': 'Image generation completed',
            'panel': panel.to_dict()
        }), 200
        
    except Exception as e:
        panel.status = 'failed'
        db.session.commit()
        print(f"❌ Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500


@storyboards_bp.route('/project/<int:project_id>/visual-styles', methods=['GET'])
@jwt_required()
def get_visual_styles(project_id):
    """Get visual styles for project"""
    styles = VisualStyle.query.filter_by(project_id=project_id).all()
    return jsonify({'styles': [s.to_dict() for s in styles]}), 200


@storyboards_bp.route('/project/<int:project_id>/visual-styles', methods=['POST'])
@jwt_required()
@validate_request(['style_name'])
def create_visual_style(project_id):
    """Create visual style for project"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    style = VisualStyle(
        project_id=project_id,
        style_name=data['style_name'],
        description=data.get('description'),
        reference_images=data.get('reference_images', []),
        color_palette=data.get('color_palette', []),
        mood_keywords=data.get('mood_keywords', []),
        is_primary=data.get('is_primary', False)
    )
    
    # If set as primary, unset other primary styles
    if style.is_primary:
        VisualStyle.query.filter_by(project_id=project_id, is_primary=True)\
            .update({'is_primary': False})
    
    db.session.add(style)
    log_activity(project_id, user_id, 'visual_style_created', 
                f'Created visual style: {style.style_name}')
    db.session.commit()
    
    return jsonify({
        'message': 'Visual style created',
        'style': style.to_dict()
    }), 201


@storyboards_bp.route('/project/<int:project_id>/download', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def download_storyboards(project_id):
    """Download all storyboard panels for a project as PDF"""
    from flask import send_file
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import io
    from datetime import datetime
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Get all scenes and panels
    scenes = Scene.query.filter_by(project_id=project_id).order_by(Scene.scene_number).all()
    
    if not scenes:
        return jsonify({'error': 'No scenes found for this project'}), 404
    
    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a56db'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1a56db'),
        spaceAfter=12
    )
    
    # Title page
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph(f"<b>{project.title}</b>", title_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"Storyboard", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    if project.genre:
        elements.append(Paragraph(f"Genre: {project.genre}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(PageBreak())
    
    # Add scenes and panels
    for scene in scenes:
        panels = StoryboardPanel.query.filter_by(scene_id=scene.scene_id).order_by(StoryboardPanel.panel_number).all()
        
        if panels:
            # Scene header
            elements.append(Paragraph(f"<b>Scene {scene.scene_number}</b>", heading_style))
            if scene.description:
                elements.append(Paragraph(scene.description, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
            
            # Add panels
            for panel in panels:
                # Panel info table
                panel_data = [
                    ['Panel', str(panel.panel_number)],
                    ['Shot Type', panel.shot_type or 'Medium'],
                    ['Camera Angle', panel.camera_angle or 'Eye Level'],
                ]
                
                panel_table = Table(panel_data, colWidths=[1.5*inch, 4*inch])
                panel_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ]))
                
                elements.append(panel_table)
                elements.append(Spacer(1, 0.1*inch))
                
                # Image prompt
                if panel.image_prompt:
                    elements.append(Paragraph(f"<b>Prompt:</b> {panel.image_prompt}", styles['Normal']))
                
                if panel.notes:
                    elements.append(Paragraph(f"<b>Notes:</b> {panel.notes}", styles['Normal']))
                
                elements.append(Spacer(1, 0.3*inch))
            
            elements.append(PageBreak())
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Generate filename
    filename = f"{project.title.replace(' ', '_')}_Storyboard_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@storyboards_bp.route('/project/<int:project_id>/mood-board', methods=['POST'])
@jwt_required()
@project_permission_required('editor')
def generate_mood_board(project_id):
    """Generate mood board for project with multiple reference images"""
    user_id = get_jwt_identity()
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json() or {}
    num_images = data.get('num_images', 4)
    
    if num_images < 1 or num_images > 8:
        return jsonify({'error': 'num_images must be between 1 and 8'}), 400
    
    print(f"🎨 Generating mood board for project: {project.title}")
    print(f"   Images requested: {num_images}")
    
    try:
        gemini_service = GeminiService()
        
        # Generate mood board
        mood_board = gemini_service.generate_mood_board(
            project_title=project.title,
            genre=project.genre or 'Film',
            logline=project.logline or '',
            num_images=num_images
        )
        
        if not mood_board:
            return jsonify({
                'error': 'Mood board generation failed. Please try again.'
            }), 500
        
        # Log AI processing
        from models import AIProcessingLog
        ai_log = AIProcessingLog(
            project_id=project_id,
            user_id=user_id,
            operation_type='mood_board_generation',
            input_data={
                'title': project.title,
                'genre': project.genre,
                'num_images': num_images
            },
            output_data={
                'images_generated': len(mood_board),
                'categories': [img['category'] for img in mood_board]
            },
            ai_model='Pollinations.ai + Gemini Pro',
            status='completed'
        )
        db.session.add(ai_log)
        
        log_activity(project_id, user_id, 'mood_board_generated', 
                    f'Generated mood board with {len(mood_board)} images')
        db.session.commit()
        
        return jsonify({
            'message': f'Mood board generated with {len(mood_board)} images',
            'mood_board': mood_board,
            'total_images': len(mood_board)
        }), 200
        
    except Exception as e:
        print(f"❌ Error generating mood board: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Mood board generation failed: {str(e)}'}), 500


@storyboards_bp.route('/project/<int:project_id>/batch-generate', methods=['POST'])
@jwt_required()
@project_permission_required('editor')
def batch_generate_storyboards(project_id):
    """Batch generate storyboard images for all pending panels"""
    user_id = get_jwt_identity()
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Get all scenes for the project
    scenes = Scene.query.filter_by(project_id=project_id).all()
    scene_ids = [s.scene_id for s in scenes]
    
    # Get all pending panels
    pending_panels = StoryboardPanel.query.filter(
        StoryboardPanel.scene_id.in_(scene_ids),
        StoryboardPanel.status == 'pending'
    ).all()
    
    if not pending_panels:
        return jsonify({'message': 'No pending panels to generate'}), 200
    
    print(f"🎨 Batch generating {len(pending_panels)} storyboard images")
    
    try:
        gemini_service = GeminiService()
        
        generated = 0
        failed = 0
        
        for panel in pending_panels:
            print(f"\n📸 Generating image for panel {panel.panel_id}...")
            
            panel.status = 'generating'
            db.session.commit()
            
            try:
                image_data = gemini_service.generate_image(
                    prompt=panel.image_prompt,
                    negative_prompt=panel.negative_prompt or "blurry, bad quality, distorted, text, watermark"
                )
                
                if image_data:
                    panel.generated_image_url = image_data
                    panel.status = 'completed'
                    panel.generation_timestamp = db.func.now()
                    panel.ai_model_used = 'Pollinations.ai'
                    generated += 1
                    print(f"   ✅ Panel {panel.panel_id} generated successfully")
                else:
                    panel.status = 'failed'
                    failed += 1
                    print(f"   ❌ Panel {panel.panel_id} generation failed")
                
                db.session.commit()
                
                # Small delay between generations
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error generating panel {panel.panel_id}: {e}")
                panel.status = 'failed'
                failed += 1
                db.session.commit()
        
        log_activity(project_id, user_id, 'batch_storyboard_generated', 
                    f'Batch generated {generated} storyboard images ({failed} failed)')
        
        return jsonify({
            'message': f'Batch generation complete',
            'generated': generated,
            'failed': failed,
            'total': len(pending_panels)
        }), 200
        
    except Exception as e:
        print(f"❌ Batch generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Batch generation failed: {str(e)}'}), 500

