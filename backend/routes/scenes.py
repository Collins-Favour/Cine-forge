"""
Scene Management Routes
Handles scene CRUD, scene breakdown, and AI suggestions
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Scene, SceneCharacter, Character
from utils.decorators import validate_request, project_permission_required
from utils.helpers import log_activity, paginate_query
from services import GroqService, GeminiService

scenes_bp = Blueprint('scenes', __name__)


@scenes_bp.route('/project/<int:project_id>/scenes', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def get_scenes(project_id):
    """Get all scenes for a project"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    query = Scene.query.filter_by(project_id=project_id)\
        .order_by(Scene.scene_number)
    
    result = paginate_query(query, page, per_page)
    
    return jsonify({
        'scenes': [s.to_dict(include_relationships=True) for s in result['items']],
        'pagination': result['pagination']
    }), 200


@scenes_bp.route('/project/<int:project_id>/scenes/<int:scene_id>', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def get_scene(project_id, scene_id):
    """Get specific scene with details"""
    scene = Scene.query.filter_by(
        scene_id=scene_id,
        project_id=project_id
    ).first()
    
    if not scene:
        return jsonify({'error': 'Scene not found'}), 404
    
    return jsonify({'scene': scene.to_dict(include_relationships=True)}), 200


@scenes_bp.route('/project/<int:project_id>/scenes', methods=['POST'])
@jwt_required()
@project_permission_required('writer')
@validate_request(['scene_number', 'description'])
def create_scene(project_id):
    """Create new scene"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Check scene limit
    from models import SystemSetting
    max_scenes = SystemSetting.query.filter_by(setting_key='max_scenes_per_project').first()
    if max_scenes:
        scene_count = Scene.query.filter_by(project_id=project_id).count()
        if scene_count >= max_scenes.get_value():
            return jsonify({'error': 'Maximum scenes limit reached'}), 403
    
    # Check if scene number already exists
    existing = Scene.query.filter_by(
        project_id=project_id,
        scene_number=data['scene_number']
    ).first()
    
    if existing:
        return jsonify({'error': 'Scene number already exists'}), 409
    
    scene = Scene(
        project_id=project_id,
        scene_number=data['scene_number'],
        slug=data.get('slug'),
        description=data['description'],
        location=data.get('location'),
        time_of_day=data.get('time_of_day', 'day'),
        interior_exterior=data.get('interior_exterior', 'INT'),
        page_length=data.get('page_length'),
        estimated_duration=data.get('estimated_duration'),
        narrative_purpose=data.get('narrative_purpose'),
        emotional_tone=data.get('emotional_tone'),
        pacing=data.get('pacing', 'medium'),
        is_action_scene=data.get('is_action_scene', False),
        is_dialogue_heavy=data.get('is_dialogue_heavy', False),
        vfx_required=data.get('vfx_required', False)
    )
    
    db.session.add(scene)
    db.session.flush()
    
    # Add characters to scene if provided
    if 'character_ids' in data:
        for char_id in data['character_ids']:
            scene_char = SceneCharacter(
                scene_id=scene.scene_id,
                character_id=char_id
            )
            db.session.add(scene_char)
    
    log_activity(project_id, user_id, 'scene_created', 
                f'Created scene {scene.scene_number}', 'scene', scene.scene_id)
    db.session.commit()
    
    return jsonify({
        'message': 'Scene created successfully',
        'scene': scene.to_dict()
    }), 201


@scenes_bp.route('/project/<int:project_id>/scenes/<int:scene_id>', methods=['PUT'])
@jwt_required()
@project_permission_required('writer')
def update_scene(project_id, scene_id):
    """Update scene"""
    user_id = get_jwt_identity()
    scene = Scene.query.filter_by(
        scene_id=scene_id,
        project_id=project_id
    ).first()
    
    if not scene:
        return jsonify({'error': 'Scene not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    updatable_fields = ['scene_number', 'slug', 'description', 'location', 'time_of_day',
                       'interior_exterior', 'page_length', 'estimated_duration', 
                       'narrative_purpose', 'emotional_tone', 'pacing', 'location_suggestion',
                       'mood_suggestion', 'lighting_suggestion', 'cinematography_notes',
                       'sound_design_notes', 'is_action_scene', 'is_dialogue_heavy', 'vfx_required']
    
    for field in updatable_fields:
        if field in data:
            setattr(scene, field, data[field])
    
    log_activity(project_id, user_id, 'scene_updated', 
                f'Updated scene {scene.scene_number}')
    db.session.commit()
    
    return jsonify({
        'message': 'Scene updated successfully',
        'scene': scene.to_dict()
    }), 200


@scenes_bp.route('/project/<int:project_id>/scenes/<int:scene_id>', methods=['DELETE'])
@jwt_required()
@project_permission_required('writer')
def delete_scene(project_id, scene_id):
    """Delete scene"""
    user_id = get_jwt_identity()
    scene = Scene.query.filter_by(
        scene_id=scene_id,
        project_id=project_id
    ).first()
    
    if not scene:
        return jsonify({'error': 'Scene not found'}), 404
    
    scene_number = scene.scene_number
    db.session.delete(scene)
    log_activity(project_id, user_id, 'scene_deleted', 
                f'Deleted scene {scene_number}')
    db.session.commit()
    
    return jsonify({'message': 'Scene deleted successfully'}), 200


@scenes_bp.route('/project/<int:project_id>/scenes/<int:scene_id>/analyze', methods=['POST'])
@jwt_required()
@project_permission_required('writer')
def analyze_scene(project_id, scene_id):
    """Generate AI suggestions for scene"""
    user_id = get_jwt_identity()
    scene = Scene.query.filter_by(
        scene_id=scene_id,
        project_id=project_id
    ).first()
    
    if not scene:
        return jsonify({'error': 'Scene not found'}), 404
    
    try:
        groq_service = GroqService()
        gemini_service = GeminiService()
        
        # Generate scene analysis
        scene_analysis = groq_service.generate_scene_description(scene.description)
        mood_analysis = gemini_service.analyze_scene_for_mood(scene.description)
        location_suggestions = groq_service.suggest_locations(scene.description)
        
        # Update scene with suggestions
        if scene_analysis:
            scene.cinematography_notes = scene_analysis
        if mood_analysis:
            scene.mood_suggestion = mood_analysis.get('analysis', '')
        if location_suggestions:
            scene.location_suggestion = str(location_suggestions)
        
        # Log AI processing
        from models import AIProcessingLog
        ai_log = AIProcessingLog(
            project_id=project_id,
            user_id=user_id,
            operation_type='scene_breakdown',
            input_data={'scene_id': scene_id},
            output_data={'scene_analysis': scene_analysis, 'mood': mood_analysis, 'locations': location_suggestions},
            ai_model='Groq + Gemini',
            status='completed'
        )
        db.session.add(ai_log)
        log_activity(project_id, user_id, 'scene_analyzed', f'AI analyzed scene {scene.scene_number}')
        db.session.commit()
        
        return jsonify({
            'message': 'Scene analyzed successfully',
            'scene': scene.to_dict(),
            'analysis': {'cinematography': scene_analysis, 'mood': mood_analysis, 'locations': location_suggestions}
        }), 200
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@scenes_bp.route('/project/<int:project_id>/scenes/<int:scene_id>/characters', methods=['POST'])
@jwt_required()
@project_permission_required('writer')
@validate_request(['character_id'])
def add_character_to_scene(project_id, scene_id):
    """Add character to scene"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    scene = Scene.query.filter_by(scene_id=scene_id, project_id=project_id).first()
    if not scene:
        return jsonify({'error': 'Scene not found'}), 404
    
    character = Character.query.filter_by(character_id=data['character_id'], project_id=project_id).first()
    if not character:
        return jsonify({'error': 'Character not found'}), 404
    
    existing = SceneCharacter.query.filter_by(scene_id=scene_id, character_id=data['character_id']).first()
    if existing:
        return jsonify({'error': 'Character already in scene'}), 409
    
    scene_char = SceneCharacter(
        scene_id=scene_id,
        character_id=data['character_id'],
        dialogue_lines=data.get('dialogue_lines', 0),
        is_main_focus=data.get('is_main_focus', False)
    )
    
    db.session.add(scene_char)
    log_activity(project_id, user_id, 'scene_character_added', f'Added {character.character_name} to scene {scene.scene_number}')
    db.session.commit()
    
    return jsonify({'message': 'Character added to scene', 'scene_character': scene_char.to_dict()}), 201


@scenes_bp.route('/project/<int:project_id>/scenes/<int:scene_id>/characters/<int:scene_character_id>', methods=['DELETE'])
@jwt_required()
@project_permission_required('writer')
def remove_character_from_scene(project_id, scene_id, scene_character_id):
    """Remove character from scene"""
    user_id = get_jwt_identity()
    scene_char = SceneCharacter.query.filter_by(scene_character_id=scene_character_id, scene_id=scene_id).first()
    
    if not scene_char:
        return jsonify({'error': 'Scene character not found'}), 404
    
    db.session.delete(scene_char)
    log_activity(project_id, user_id, 'scene_character_removed', 'Removed character from scene')
    db.session.commit()
    
    return jsonify({'message': 'Character removed from scene'}), 200
