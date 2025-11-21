"""
Script Management Routes
Handles script versions, character extraction, and script analysis
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, ScriptVersion, Character, Project
from utils.decorators import validate_request, project_permission_required
from utils.helpers import log_activity, calculate_script_stats, paginate_query
from services import GroqService
from datetime import datetime

scripts_bp = Blueprint('scripts', __name__)


@scripts_bp.route('/project/<int:project_id>/versions', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def get_script_versions(project_id):
    """Get all script versions for a project"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = ScriptVersion.query.filter_by(project_id=project_id)\
        .order_by(ScriptVersion.version_number.desc())
    
    result = paginate_query(query, page, per_page)
    
    return jsonify({
        'versions': [v.to_dict() for v in result['items']],
        'pagination': result['pagination']
    }), 200


@scripts_bp.route('/project/<int:project_id>/versions/<int:version_id>', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def get_script_version(project_id, version_id):
    """Get specific script version with content"""
    version = ScriptVersion.query.filter_by(
        version_id=version_id,
        project_id=project_id
    ).first()
    
    if not version:
        return jsonify({'error': 'Script version not found'}), 404
    
    return jsonify({'version': version.to_dict(include_content=True)}), 200


@scripts_bp.route('/project/<int:project_id>/versions', methods=['POST'])
@jwt_required()
@project_permission_required('writer')
@validate_request(['script_content'])
def create_script_version(project_id):
    """Create new script version"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get latest version number
    latest_version = ScriptVersion.query.filter_by(project_id=project_id)\
        .order_by(ScriptVersion.version_number.desc()).first()
    
    next_version_number = 1 if not latest_version else latest_version.version_number + 1
    
    # Calculate stats
    stats = calculate_script_stats(data['script_content'])
    
    # Create version
    version = ScriptVersion(
        project_id=project_id,
        script_content=data['script_content'],
        version_number=next_version_number,
        version_name=data.get('version_name', f'Version {next_version_number}'),
        word_count=stats['word_count'],
        page_count=stats['page_count'],
        estimated_runtime=stats['estimated_runtime'],
        changes_summary=data.get('changes_summary'),
        created_by=user_id
    )
    
    db.session.add(version)
    log_activity(project_id, user_id, 'script_version_created', 
                f'Created script version {next_version_number}', 'script_version', version.version_id)
    db.session.commit()
    
    return jsonify({
        'message': 'Script version created successfully',
        'version': version.to_dict()
    }), 201


@scripts_bp.route('/project/<int:project_id>/versions/<int:version_id>', methods=['PUT'])
@jwt_required()
@project_permission_required('writer')
def update_script_version(project_id, version_id):
    """Update script version"""
    user_id = get_jwt_identity()
    version = ScriptVersion.query.filter_by(
        version_id=version_id,
        project_id=project_id
    ).first()
    
    if not version:
        return jsonify({'error': 'Script version not found'}), 404
    
    data = request.get_json()
    
    if 'script_content' in data:
        stats = calculate_script_stats(data['script_content'])
        version.script_content = data['script_content']
        version.word_count = stats['word_count']
        version.page_count = stats['page_count']
        version.estimated_runtime = stats['estimated_runtime']
    
    if 'version_name' in data:
        version.version_name = data['version_name']
    
    if 'changes_summary' in data:
        version.changes_summary = data['changes_summary']
    
    log_activity(project_id, user_id, 'script_version_updated', 
                f'Updated script version {version.version_number}')
    db.session.commit()
    
    return jsonify({
        'message': 'Script version updated successfully',
        'version': version.to_dict()
    }), 200


@scripts_bp.route('/project/<int:project_id>/versions/<int:version_id>/analyze', methods=['POST'])
@jwt_required()
@project_permission_required('writer')
def analyze_script(project_id, version_id):
    """Analyze script using AI"""
    user_id = get_jwt_identity()
    version = ScriptVersion.query.filter_by(
        version_id=version_id,
        project_id=project_id
    ).first()
    
    if not version:
        return jsonify({'error': 'Script version not found'}), 404
    
    try:
        groq_service = GroqService()
        analysis = groq_service.analyze_script(version.script_content)
        
        if not analysis:
            return jsonify({'error': 'Failed to analyze script'}), 500
        
        # Log AI processing
        from models import AIProcessingLog
        ai_log = AIProcessingLog(
            project_id=project_id,
            user_id=user_id,
            operation_type='script_analysis',
            input_data={'version_id': version_id},
            output_data=analysis,
            ai_model='Groq Mixtral',
            status='completed'
        )
        db.session.add(ai_log)
        
        log_activity(project_id, user_id, 'script_analyzed', 
                    f'Analyzed script version {version.version_number}')
        db.session.commit()
        
        return jsonify({
            'message': 'Script analyzed successfully',
            'analysis': analysis
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@scripts_bp.route('/project/<int:project_id>/characters', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def get_characters(project_id):
    """Get all characters for a project"""
    characters = Character.query.filter_by(project_id=project_id)\
        .order_by(Character.character_name).all()
    
    return jsonify({
        'characters': [c.to_dict() for c in characters]
    }), 200


@scripts_bp.route('/project/<int:project_id>/characters', methods=['POST'])
@jwt_required()
@project_permission_required('writer')
@validate_request(['character_name'])
def create_character(project_id):
    """Create new character"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Check if character already exists
    existing = Character.query.filter_by(
        project_id=project_id,
        character_name=data['character_name']
    ).first()
    
    if existing:
        return jsonify({'error': 'Character already exists'}), 409
    
    character = Character(
        project_id=project_id,
        character_name=data['character_name'],
        description=data.get('description'),
        role_type=data.get('role_type', 'supporting'),
        age_range=data.get('age_range'),
        gender=data.get('gender'),
        personality_traits=data.get('personality_traits'),
        dialogue_count=data.get('dialogue_count', 0),
        first_appearance=data.get('first_appearance')
    )
    
    db.session.add(character)
    log_activity(project_id, user_id, 'character_created', 
                f'Created character: {character.character_name}', 'character', character.character_id)
    db.session.commit()
    
    return jsonify({
        'message': 'Character created successfully',
        'character': character.to_dict()
    }), 201


@scripts_bp.route('/project/<int:project_id>/characters/<int:character_id>', methods=['PUT'])
@jwt_required()
@project_permission_required('writer')
def update_character(project_id, character_id):
    """Update character"""
    user_id = get_jwt_identity()
    character = Character.query.filter_by(
        character_id=character_id,
        project_id=project_id
    ).first()
    
    if not character:
        return jsonify({'error': 'Character not found'}), 404
    
    data = request.get_json()
    
    if 'character_name' in data:
        character.character_name = data['character_name']
    if 'description' in data:
        character.description = data['description']
    if 'role_type' in data:
        character.role_type = data['role_type']
    if 'age_range' in data:
        character.age_range = data['age_range']
    if 'gender' in data:
        character.gender = data['gender']
    if 'personality_traits' in data:
        character.personality_traits = data['personality_traits']
    if 'dialogue_count' in data:
        character.dialogue_count = data['dialogue_count']
    if 'first_appearance' in data:
        character.first_appearance = data['first_appearance']
    
    log_activity(project_id, user_id, 'character_updated', 
                f'Updated character: {character.character_name}')
    db.session.commit()
    
    return jsonify({
        'message': 'Character updated successfully',
        'character': character.to_dict()
    }), 200


@scripts_bp.route('/project/<int:project_id>/characters/<int:character_id>', methods=['DELETE'])
@jwt_required()
@project_permission_required('writer')
def delete_character(project_id, character_id):
    """Delete character"""
    user_id = get_jwt_identity()
    character = Character.query.filter_by(
        character_id=character_id,
        project_id=project_id
    ).first()
    
    if not character:
        return jsonify({'error': 'Character not found'}), 404
    
    character_name = character.character_name
    db.session.delete(character)
    log_activity(project_id, user_id, 'character_deleted', 
                f'Deleted character: {character_name}')
    db.session.commit()
    
    return jsonify({'message': 'Character deleted successfully'}), 200
