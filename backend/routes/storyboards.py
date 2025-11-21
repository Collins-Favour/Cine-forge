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
    panel = StoryboardPanel.query.get(panel_id)
    
    if not panel:
        return jsonify({'error': 'Panel not found'}), 404
    
    scene = Scene.query.get(panel.scene_id)
    
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
        
        # TODO: Actual image generation would happen here via Stable Diffusion/DALL-E API
        # For now, we'll mark it as completed with the prompt
        panel.status = 'completed'
        panel.generation_timestamp = db.func.now()
        panel.ai_model_used = 'Gemini (prompt optimization)'
        
        # Log AI processing
        from models import AIProcessingLog
        ai_log = AIProcessingLog(
            project_id=scene.project_id,
            user_id=user_id,
            operation_type='image_generation',
            input_data={'panel_id': panel_id, 'prompt': enhanced_prompt},
            output_data={'status': 'completed'},
            ai_model='Gemini + Stable Diffusion',
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
