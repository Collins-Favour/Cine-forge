"""
Project Routes
Handles project CRUD operations and management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, func
from sqlalchemy.orm import selectinload, joinedload
from models import db, Project, ProjectCollaborator, ActivityLog, User, Scene, Character, ScriptVersion
from utils.decorators import validate_request, project_permission_required
from utils.helpers import log_activity
from utils.cache import cache_get, cache_set, cache_key, invalidate_project_cache
from datetime import datetime
from utils.logger import get_logger

projects_bp = Blueprint('projects', __name__)
logger = get_logger('cineforge.api')


@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    """Get all projects for current user with optimized queries"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Try cache first
        cache_k = cache_key('projects', 'user', user_id, 'page', page, 'per_page', per_page)
        cached_result = cache_get(cache_k)
        if cached_result:
            logger.debug(f"Using cached projects for user {user_id}")
            return jsonify(cached_result), 200
        
        logger.debug(f"Fetching projects for user_id: {user_id} (type: {type(user_id).__name__})")
        
        # Get collaborated project IDs - must have accepted invitation
        collaborations = ProjectCollaborator.query.filter(
            ProjectCollaborator.user_id == user_id,
            ProjectCollaborator.invitation_status == 'accepted'
        ).all()
        collab_project_ids = [c.project_id for c in collaborations if c.project_id]
        logger.debug(f"Collaborated project IDs: {collab_project_ids}")
        
        # Build query to get all projects (owned or collaborated) in one query
        if collab_project_ids:
            # User owns OR is collaborator on the project
            all_projects_query = Project.query.filter(
                or_(
                    Project.created_by == user_id,
                    Project.project_id.in_(collab_project_ids)
                ),
                Project.is_archived == False
            )
        else:
            # Only owned projects
            all_projects_query = Project.query.filter(
                Project.created_by == user_id,
                Project.is_archived == False
            )
        
        # Order and paginate
        all_projects = all_projects_query\
            .order_by(Project.updated_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        logger.debug(f"Total projects returned: {len(all_projects.items)}")
        
        # Bulk compute stats for all projects to avoid N+1 queries
        project_ids = [p.project_id for p in all_projects.items]
        
        if project_ids:
            # Get all stats in one query each
            scene_counts = db.session.query(
                Scene.project_id,
                func.count(Scene.scene_id).label('count')
            ).filter(Scene.project_id.in_(project_ids))\
             .group_by(Scene.project_id).all()
            
            character_counts = db.session.query(
                Character.project_id,
                func.count(Character.character_id).label('count')
            ).filter(Character.project_id.in_(project_ids))\
             .group_by(Character.project_id).all()
            
            collaborator_counts = db.session.query(
                ProjectCollaborator.project_id,
                func.count(ProjectCollaborator.collaboration_id).label('count')
            ).filter(ProjectCollaborator.project_id.in_(project_ids))\
             .group_by(ProjectCollaborator.project_id).all()
            
            latest_versions = db.session.query(
                ScriptVersion.project_id,
                func.max(ScriptVersion.version_number).label('version')
            ).filter(ScriptVersion.project_id.in_(project_ids))\
             .group_by(ScriptVersion.project_id).all()
            
            # Create lookup dictionaries
            scene_dict = {pid: count for pid, count in scene_counts}
            character_dict = {pid: count for pid, count in character_counts}
            collab_dict = {pid: count for pid, count in collaborator_counts}
            version_dict = {pid: version for pid, version in latest_versions}
        else:
            scene_dict = {}
            character_dict = {}
            collab_dict = {}
            version_dict = {}
        
        # Separate owned and collaborated projects for frontend
        owned_projects = []
        collaborated_projects = []
        
        for project in all_projects.items:
            # Pre-compute stats for this project
            stats_data = {
                'total_scenes': scene_dict.get(project.project_id, 0),
                'total_characters': character_dict.get(project.project_id, 0),
                'total_collaborators': collab_dict.get(project.project_id, 0),
                'latest_script_version': version_dict.get(project.project_id, 0)
            }
            
            if project.created_by == user_id:
                owned_projects.append(project.to_dict(include_stats=True, stats_data=stats_data))
            else:
                collaborated_projects.append(project.to_dict(include_stats=True, stats_data=stats_data))
        
        logger.debug(f"Owned: {len(owned_projects)}, Collaborated: {len(collaborated_projects)}")
        
        # Build all projects list with stats
        all_projects_list = owned_projects + collaborated_projects
        
        result = {
            'projects': all_projects_list,
            'owned_projects': owned_projects,
            'collaborated_projects': collaborated_projects,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': all_projects.total,
                'pages': all_projects.pages
            }
        }
        
        # Cache for 2 minutes
        cache_set(cache_k, result, timeout=120)
        
        return jsonify(result), 200
    except ValueError as ve:
        logger.error(f"ValueError in get_projects: {str(ve)}")
        return jsonify({'error': 'Invalid user identity'}), 400
    except Exception as e:
        logger.error(f"Error in get_projects: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to fetch projects: {str(e)}'}), 500


@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def get_project(project_id):
    """Get project by ID with optimized stats"""
    # Try cache first
    cache_k = cache_key('project', project_id)
    cached_result = cache_get(cache_k)
    if cached_result:
        return jsonify({'project': cached_result}), 200
    
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Compute stats in one query each
    stats_data = {
        'total_scenes': Scene.query.filter_by(project_id=project_id).count(),
        'total_characters': Character.query.filter_by(project_id=project_id).count(),
        'total_collaborators': ProjectCollaborator.query.filter_by(project_id=project_id).count(),
        'latest_script_version': db.session.query(func.max(ScriptVersion.version_number))\
            .filter(ScriptVersion.project_id == project_id).scalar() or 0
    }
    
    project_data = project.to_dict(include_stats=True, stats_data=stats_data)
    
    # Cache for 5 minutes
    cache_set(cache_k, project_data, timeout=300)
    
    return jsonify({'project': project_data}), 200


@projects_bp.route('', methods=['POST'])
@jwt_required()
@validate_request(['title'])
def create_project():
    """Create new project"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Project limit check disabled - unlimited projects for all users
    # from models import User, SystemSetting
    # user = User.query.get(user_id)
    # if user.role != 'professional' and user.role != 'admin':
    #     max_projects = SystemSetting.query.filter_by(setting_key='max_free_projects').first()
    #     if max_projects:
    #         project_count = Project.query.filter_by(created_by=user_id, is_archived=False).count()
    #         if project_count >= max_projects.get_value():
    #             return jsonify({'error': 'Project limit reached. Upgrade to create more projects.'}), 403
    
    project = Project(
        title=data['title'],
        logline=data.get('logline'),
        synopsis=data.get('synopsis'),
        genre=data.get('genre'),
        target_length=data.get('target_length'),
        budget_range=data.get('budget_range'),
        created_by=user_id
    )
    
    db.session.add(project)
    db.session.flush()
    
    # Add creator as owner
    collaborator = ProjectCollaborator(
        project_id=project.project_id,
        user_id=user_id,
        role='owner',
        invited_by=user_id,
        invitation_status='accepted',
        joined_at=datetime.utcnow()
    )
    db.session.add(collaborator)
    
    # Log activity
    log_activity(project.project_id, user_id, 'project_created', f'Created project: {project.title}')
    
    db.session.commit()
    
    # Auto-generate script and storyboard if synopsis/description provided
    script_generated = False
    if data.get('synopsis') or data.get('logline'):
        logger.info(f"Starting AI generation for project {project.project_id}...")
        try:
            from services import GroqService
            from models import ScriptVersion
            
            logger.info(" Initializing Groq service...")
            groq_service = GroqService()
            
            logger.debug(" Generating screenplay with Groq AI...")
            # Generate screenplay using Groq AI with mood and lighting suggestions
            script_analysis = groq_service.generate_screenplay(
                title=data['title'],
                synopsis=data.get('synopsis', ''),
                genre=data.get('genre', 'Drama'),
                logline=data.get('logline', '')
            )
            
            logger.debug(f"Script generation result: {script_analysis is not None}")
            
            if script_analysis:
                logger.info(" Script generation successful, creating script version...")
                # Create formatted script content from analysis
                script_content = format_enhanced_screenplay(
                    title=data['title'],
                    genre=data.get('genre', 'Drama'),
                    logline=data.get('logline', ''),
                    script_analysis=script_analysis
                )
                
                # Create first script version
                script_version = ScriptVersion(
                    project_id=project.project_id,
                    script_content=script_content,
                    version_number=1,
                    created_by=user_id,
                    changes_summary='Auto-generated from project synopsis'
                )
                db.session.add(script_version)
                db.session.flush()
                
                # Log AI processing
                from models import AIProcessingLog
                ai_log = AIProcessingLog(
                    project_id=project.project_id,
                    user_id=user_id,
                    operation_type='auto_script_generation',
                    input_data={'synopsis': data.get('synopsis'), 'logline': data.get('logline')},
                    output_data=script_analysis,
                    ai_model='Groq Llama 3.3 70B',
                    status='completed'
                )
                db.session.add(ai_log)
                
                log_activity(project.project_id, user_id, 'script_generated', 
                           'AI generated script from synopsis')
                
                script_generated = True
                
                # Auto-generate scenes and ONE storyboard panel
                if script_analysis.get('scenes'):
                    from models import Scene, StoryboardPanel
                    from services import GroqService as _GroqService, ImageGenerationService
                    
                    groq_svc = _GroqService()
                    
                    # Create all scenes
                    for i, scene_data in enumerate(script_analysis['scenes'], 1):
                        scene_desc = scene_data.get('description', str(scene_data)) if isinstance(scene_data, dict) else str(scene_data)
                        scene = Scene(
                            project_id=project.project_id,
                            scene_number=i,
                            slug=f"scene-{i}",
                            description=scene_desc[:500]
                        )
                        db.session.add(scene)
                    
                    db.session.flush()
                    
                    # Only create ONE storyboard panel from the first scene
                    first_scene = Scene.query.filter_by(project_id=project.project_id, scene_number=1).first()
                    if first_scene:
                        first_scene_data = script_analysis['scenes'][0]
                        scene_desc = first_scene_data.get('description', str(first_scene_data)) if isinstance(first_scene_data, dict) else str(first_scene_data)
                        
                        # Generate storyboard prompt using title and synopsis
                        prompt_base = f"{data['title']}: {data.get('synopsis', data.get('logline', ''))}"
                        image_prompt = groq_svc.generate_storyboard_prompt(
                            f"{prompt_base}\\n\\nOpening Scene: {scene_desc}",
                            style=data.get('genre', 'cinematic').lower()
                        )
                        
                        if not image_prompt:
                            image_prompt = f"Cinematic {data.get('genre', 'film')} opening scene: {scene_desc[:200]}"
                        
                        # Create single storyboard panel
                        panel = StoryboardPanel(
                            scene_id=first_scene.scene_id,
                            panel_number=1,
                            image_prompt=image_prompt,
                            style_reference=data.get('genre', 'cinematic'),
                            status='pending',
                            shot_type='establishing'
                        )
                        db.session.add(panel)
                    
                    log_activity(project.project_id, user_id, 'storyboard_generated', 
                               'AI generated opening storyboard panel')
                
                db.session.commit()
        except Exception as e:
            # Don't fail project creation if AI generation fails
            logger.error(f"AI generation error: {e}", exc_info=True)
            db.session.rollback()
            db.session.commit()
    else:
        logger.warning(" No synopsis or logline provided, skipping AI generation")
    
    response_data = {
        'message': 'Project created successfully',
        'project': project.to_dict()
    }
    
    if script_generated:
        logger.info(" AI generation completed successfully!")
        response_data['message'] += ' with AI-generated script and storyboard'
        response_data['ai_generated'] = True
    
    # Invalidate user's project cache
    from utils.cache import invalidate_user_cache
    invalidate_user_cache(user_id)
    
    return jsonify(response_data), 201


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
@project_permission_required('editor')
def update_project(project_id):
    """Update project"""
    project = Project.query.get(project_id)
    user_id = int(get_jwt_identity())
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'title' in data:
        project.title = data['title']
    if 'logline' in data:
        project.logline = data['logline']
    if 'synopsis' in data:
        project.synopsis = data['synopsis']
    if 'genre' in data:
        project.genre = data['genre']
    if 'target_length' in data:
        project.target_length = data['target_length']
    if 'budget_range' in data:
        project.budget_range = data['budget_range']
    if 'production_stage' in data:
        project.production_stage = data['production_stage']
    if 'thumbnail_url' in data:
        project.thumbnail_url = data['thumbnail_url']
    if 'is_public' in data:
        project.is_public = data['is_public']
    
    log_activity(project_id, user_id, 'project_updated', 'Updated project details')
    
    db.session.commit()
    
    # Invalidate caches
    invalidate_project_cache(project_id)
    from utils.cache import invalidate_user_cache
    invalidate_user_cache(project.created_by)
    
    return jsonify({
        'message': 'Project updated successfully',
        'project': project.to_dict()
    }), 200


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
@project_permission_required('owner')
def delete_project(project_id):
    """Delete project (soft delete)"""
    project = Project.query.get(project_id)
    user_id = int(get_jwt_identity())
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    project.is_archived = True
    db.session.commit()
    
    # Invalidate caches
    invalidate_project_cache(project_id)
    from utils.cache import invalidate_user_cache
    invalidate_user_cache(project.created_by)
    
    return jsonify({'message': 'Project archived successfully'}), 200


@projects_bp.route('/<int:project_id>/collaborators', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def get_collaborators(project_id):
    """Get project collaborators"""
    collaborators = ProjectCollaborator.query.filter_by(project_id=project_id).all()
    
    result = []
    for collab in collaborators:
        from models import User
        user = User.query.get(collab.user_id)
        if user:
            collab_data = collab.to_dict()
            collab_data['user'] = user.to_dict()
            result.append(collab_data)
    
    return jsonify({'collaborators': result}), 200


@projects_bp.route('/<int:project_id>/collaborators', methods=['POST'])
@jwt_required()
@project_permission_required('owner')
@validate_request(['role'])
def add_collaborator(project_id):
    """Add collaborator to project"""
    data = request.get_json()
    user_id = int(get_jwt_identity())

    # Support inviting by `email` (recommended) or by `user_id` (legacy)
    target_user = None

    if 'email' in data and data.get('email'):
        from flask import current_app
        target_user = User.query.filter_by(email=data['email'].lower()).first()
        if not target_user:
            return jsonify({'error': 'User not found. They must register before being invited.'}), 404
    else:
        target_user = User.query.get(data.get('user_id'))
        if not target_user:
            return jsonify({'error': 'User not found'}), 404

    # Check if already collaborator
    existing = ProjectCollaborator.query.filter_by(
        project_id=project_id,
        user_id=target_user.user_id
    ).first()

    if existing:
        return jsonify({'error': 'User is already a collaborator'}), 409

    collaborator = ProjectCollaborator(
        project_id=project_id,
        user_id=target_user.user_id,
        role=data['role'],
        invited_by=user_id,
        invitation_status='pending'
    )

    db.session.add(collaborator)
    db.session.flush()  # Get the collaboration_id
    
    logger.debug(f"Creating collaboration invite: project_id={project_id}, invited_user_id={target_user.user_id}, inviter_id={user_id}, collaboration_id={collaborator.collaboration_id}")
    
    # Create an in-app notification for the invited user
    try:
        import json
        from models import Notification
        project = Project.query.get(project_id)
        inviter = User.query.get(user_id)
        
        logger.debug(f"Creating notification for user_id={target_user.user_id} (email: {target_user.email})")
        
        notif = Notification(
            user_id=target_user.user_id,
            notification_type='collaboration_invite',
            title=f"You've been invited to collaborate on {project.title}",
            message=f"{inviter.username} invited you to join the project as {data['role']}",
            link_url=f'/projects/{project_id}',
            action_data=json.dumps({
                'collaboration_id': collaborator.collaboration_id,
                'project_id': project_id,
                'invited_by': user_id,
                'role': data['role']
            })
        )
        db.session.add(notif)
        db.session.flush()
        
        logger.info(f"Notification created: notification_id={notif.notification_id}")
        
        # Send real-time notification via socket if available
        try:
            from app import socketio
            socketio.emit('new_notification', {
                'notification': notif.to_dict(),
                'user_id': target_user.user_id
            }, room=f'user_{target_user.user_id}')
            logger.debug(f"Real-time notification sent to user_{target_user.user_id}")
        except Exception as socket_err:
            logger.error(f"Socket notification failed (non-critical): {socket_err}")
            
    except Exception as e:
        logger.error(f"Error creating notification: {e}", exc_info=True)
        # If Notification model or DB insert fails, continue without blocking invite
        pass

    log_activity(project_id, user_id, 'collaborator_added', f'Invited user {target_user.user_id} with role: {data["role"]}')
    db.session.commit()

    # Attempt to send email if Flask-Mail is configured (optional)
    try:
        from flask import current_app
        mail_ext = current_app.extensions.get('mail') if hasattr(current_app, 'extensions') else None
        if mail_ext:
            from flask_mail import Message
            msg = Message(
                subject=f"Invitation to collaborate on {Project.query.get(project_id).title}",
                recipients=[target_user.email],
                body=f"Hi {target_user.first_name or target_user.username},\n\n{User.query.get(user_id).username} has invited you to collaborate on the project '{Project.query.get(project_id).title}' as {data['role']}.\n\nOpen the project to accept the invitation: /projects/{project_id}\n\n- CineForge Team"
            )
            try:
                mail_ext.send(msg)
            except Exception:
                # Non-fatal if email sending fails
                pass
    except Exception:
        pass

    collab_data = collaborator.to_dict()
    collab_data['user'] = target_user.to_dict()

    return jsonify({
        'message': 'Collaborator invited successfully',
        'collaborator': collab_data
    }), 201


@projects_bp.route('/<int:project_id>/collaborators/<int:collaboration_id>/respond', methods=['POST'])
@jwt_required()
@validate_request(['response'])
def respond_to_invitation(project_id, collaboration_id):
    """Accept or decline collaboration invitation"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    response = data['response']  # 'accept' or 'decline'
    
    logger.debug(f"User {user_id} responding to invitation: collaboration_id={collaboration_id}, response={response}")
    
    if response not in ['accept', 'decline']:
        return jsonify({'error': 'Response must be "accept" or "decline"'}), 400
    
    # Get the collaboration record
    collaborator = ProjectCollaborator.query.get(collaboration_id)
    
    if not collaborator:
        logger.error(f"Collaboration {collaboration_id} not found")
        return jsonify({'error': 'Invitation not found'}), 404
    
    # Verify this invitation is for the current user
    if collaborator.user_id != user_id:
        logger.error(f"User {user_id} tried to respond to invitation for user {collaborator.user_id}")
        return jsonify({'error': 'This invitation is not for you'}), 403
    
    # Verify invitation is still pending
    if collaborator.invitation_status != 'pending':
        logger.warning(f"Invitation already {collaborator.invitation_status}")
        return jsonify({'error': f'Invitation already {collaborator.invitation_status}'}), 409
    
    if response == 'accept':
        collaborator.invitation_status = 'accepted'
        collaborator.joined_at = datetime.utcnow()
        log_activity(project_id, user_id, 'collaboration_accepted', f'User accepted collaboration invitation')
        message = 'Invitation accepted successfully! You can now access the project.'
        logger.info(f"User {user_id} accepted invitation to project {project_id}")
    else:
        collaborator.invitation_status = 'declined'
        log_activity(project_id, user_id, 'collaboration_declined', f'User declined collaboration invitation')
        message = 'Invitation declined'
        logger.error(f"User {user_id} declined invitation to project {project_id}")
    
    db.session.commit()
    
    return jsonify({
        'message': message,
        'collaborator': collaborator.to_dict(),
        'status': collaborator.invitation_status
    }), 200


@projects_bp.route('/<int:project_id>/collaborators/<int:collaboration_id>', methods=['DELETE'])
@jwt_required()
@project_permission_required('owner')
def remove_collaborator(project_id, collaboration_id):
    """Remove collaborator from project"""
    collaborator = ProjectCollaborator.query.get(collaboration_id)
    user_id = int(get_jwt_identity())
    
    if not collaborator or collaborator.project_id != project_id:
        return jsonify({'error': 'Collaborator not found'}), 404
    
    if collaborator.role == 'owner':
        return jsonify({'error': 'Cannot remove project owner'}), 403
    
    db.session.delete(collaborator)
    log_activity(project_id, user_id, 'collaborator_removed', 'Removed collaborator')
    db.session.commit()
    
    return jsonify({'message': 'Collaborator removed successfully'}), 200



@projects_bp.route('/<int:project_id>/collaborators/<int:collaboration_id>', methods=['PATCH'])
@jwt_required()
@project_permission_required('owner')
@validate_request(['role'])
def update_collaborator_role(project_id, collaboration_id):
    """Update a collaborator's role (owners only). Direct ownership transfer is not allowed here."""
    data = request.get_json()
    user_id = int(get_jwt_identity())

    allowed_roles = ['owner', 'director', 'writer', 'editor', 'viewer']
    new_role = data.get('role')

    if new_role not in allowed_roles:
        return jsonify({'error': 'Invalid role specified'}), 400

    collaborator = ProjectCollaborator.query.get(collaboration_id)
    if not collaborator or collaborator.project_id != project_id:
        return jsonify({'error': 'Collaborator not found'}), 404

    # Prevent changing the existing project owner via this endpoint
    if collaborator.role == 'owner' and new_role != 'owner':
        return jsonify({'error': 'Cannot change role of the project owner via this endpoint'}), 403

    # Prevent elevating someone to owner via this simple role-change endpoint
    if new_role == 'owner' and collaborator.role != 'owner':
        return jsonify({'error': 'Use the ownership transfer endpoint to make a user the owner'}), 403

    # Update role
    collaborator.role = new_role
    log_activity(project_id, user_id, 'collaborator_role_changed', f'Changed collaborator {collaborator.user_id} role to {new_role}')
    db.session.commit()

    # Attach user info for convenience
    from models import User
    user = User.query.get(collaborator.user_id)
    collab_data = collaborator.to_dict()
    if user:
        collab_data['user'] = user.to_dict()

    return jsonify({'message': 'Collaborator role updated', 'collaborator': collab_data}), 200



@projects_bp.route('/<int:project_id>/transfer-owner', methods=['POST'])
@jwt_required()
@project_permission_required('owner')
@validate_request(['collaboration_id'])
def transfer_project_ownership(project_id):
    """Transfer project ownership to another collaborator.

    Body: { collaboration_id: <int> }
    This will set the specified collaborator's role to 'owner', demote the previous owner to 'director',
    and update `project.created_by` to the new owner's user_id. Notifications should be sent separately.
    """
    data = request.get_json()
    user_id = int(get_jwt_identity())

    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    # Find current owner collaborator entry
    current_owner = ProjectCollaborator.query.filter_by(project_id=project_id, role='owner').first()
    if not current_owner:
        return jsonify({'error': 'Current owner record not found'}), 400

    new_collab = ProjectCollaborator.query.get(data['collaboration_id'])
    if not new_collab or new_collab.project_id != project_id:
        return jsonify({'error': 'Target collaborator not found'}), 404

    if new_collab.user_id == current_owner.user_id:
        return jsonify({'error': 'Specified user is already the owner'}), 400

    # Promote target to owner
    new_collab.role = 'owner'

    # Demote previous owner to director (safe default)
    try:
        current_owner.role = 'director'
    except Exception:
        current_owner.role = 'editor'

    # Update project created_by to the new owner id
    project.created_by = new_collab.user_id

    # Log activity
    log_activity(project_id, user_id, 'ownership_transferred', f'Ownership transferred to user {new_collab.user_id}')

    db.session.commit()

    # Return updated collaborator info for convenience
    from models import User
    user = User.query.get(new_collab.user_id)
    collab_data = new_collab.to_dict()
    if user:
        collab_data['user'] = user.to_dict()

    return jsonify({'message': 'Ownership transferred', 'collaborator': collab_data}), 200


@projects_bp.route('/<int:project_id>/activity', methods=['GET'])
@jwt_required()
@project_permission_required('viewer')
def get_project_activity(project_id):
    """Get activity log for project"""
    user_id = int(get_jwt_identity())
    
    # Check if user has access to this project
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Verify user is collaborator or owner
    is_owner = project.created_by == user_id
    is_collaborator = ProjectCollaborator.query.filter_by(
        project_id=project_id, 
        user_id=user_id,
        invitation_status='accepted'
    ).first() is not None
    
    if not is_owner and not is_collaborator:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get pagination params
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    activity_type = request.args.get('type')
    
    # Build query
    query = ActivityLog.query.filter_by(project_id=project_id)
    
    if activity_type:
        query = query.filter_by(activity_type=activity_type)
    
    # Get activities with user info
    activities = query.order_by(ActivityLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Format response with user information
    activities_data = []
    for activity in activities.items:
        activity_dict = activity.to_dict()
        # Add user info
        user = User.query.get(activity.user_id)
        if user:
            activity_dict['user'] = {
                'user_id': user.user_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile_pic_url': user.profile_pic_url
            }
        activities_data.append(activity_dict)
    
    return jsonify({
        'activities': activities_data,
        'pagination': {
            'page': activities.page,
            'per_page': activities.per_page,
            'total': activities.total,
            'pages': activities.pages
        }
    }), 200


@projects_bp.route('/<int:project_id>/generate-content', methods=['POST'])
@jwt_required()
@project_permission_required('writer')
def generate_project_content(project_id):
    """Auto-generate script and storyboard for a project"""
    user_id = int(get_jwt_identity())
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Check if project has synopsis or logline
    synopsis_content = project.synopsis or project.logline
    if not synopsis_content:
        return jsonify({'error': 'Project must have a synopsis or logline for AI generation'}), 400
    
    logger.info(f"Starting content generation for project: {project.title}")
    logger.debug(f"Synopsis: {synopsis_content[:100]}...")
    
    try:
        # Initialize AI services
        from services import GroqService, ImageGenerationService
        groq_service = GroqService()
        image_service = ImageGenerationService()
        
        # 1. Generate script using Groq
        logger.debug(" Calling Groq API to generate screenplay...")
        script_analysis = groq_service.generate_screenplay(
            title=project.title,
            synopsis=synopsis_content,
            genre=project.genre or 'Drama',
            logline=project.logline or ''
        )
        
        if not script_analysis or not script_analysis.get('scenes'):
            logger.error(" Groq API returned no scenes or invalid data")
            logger.debug(f"Script analysis: {script_analysis}")
            return jsonify({
                'error': 'Script generation failed. The AI returned invalid data. Please try again or provide more details in your synopsis.'
            }), 500
        
        logger.info(f"Groq generated script with {len(script_analysis.get('scenes', []))} scenes")
        
        # Create professionally formatted script with enhanced structure
        script_content = format_enhanced_screenplay(
            title=project.title,
            genre=project.genre or 'Drama',
            logline=project.logline or '',
            script_analysis=script_analysis
        )
        
        # Save script version
        from models import ScriptVersion
        script_version = ScriptVersion(
            project_id=project_id,
            script_content=script_content,
            version_number=1,
            created_by=user_id,
            changes_summary='Auto-generated from project synopsis'
        )
        db.session.add(script_version)
        db.session.flush()
        
        # Log AI processing
        from models import AIProcessingLog
        ai_log = AIProcessingLog(
            project_id=project_id,
            user_id=user_id,
            operation_type='auto_script_generation',
            input_data={'synopsis': project.synopsis, 'logline': project.logline},
            output_data=script_analysis,
            ai_model='Groq Llama 3.3 70B',
            status='completed'
        )
        db.session.add(ai_log)
        
        # 2. Generate scenes and ONE storyboard panel
        from models import Scene, StoryboardPanel
        scenes_created = 0
        panels_created = 0
        
        if script_analysis.get('scenes'):
            # Create all scenes
            for i, scene_data in enumerate(script_analysis['scenes'], 1):
                scene_desc = scene_data.get('description', str(scene_data)) if isinstance(scene_data, dict) else str(scene_data)
                scene = Scene(
                    project_id=project_id,
                    scene_number=i,
                    slug=f"scene-{i}",
                    description=scene_desc[:500]
                )
                db.session.add(scene)
                scenes_created += 1
            
            db.session.flush()
            
            # Only create ONE storyboard panel from the first scene
            first_scene = Scene.query.filter_by(project_id=project_id, scene_number=1).first()
            if first_scene:
                try:
                    logger.debug(" Using INTELLIGENT storyboard generation (Groq-based)...")
                    logger.debug(" Analyzing project directly from logline and synopsis...")
                    
                    # Use intelligent generation that doesn't rely on Groq script
                    image_prompt = groq_service.generate_storyboard_from_project(
                        title=project.title,
                        genre=project.genre or 'Drama',
                        logline=project.logline or '',
                        synopsis=project.synopsis or ''
                    )
                    
                    # Fallback if Groq fails
                    if not image_prompt:
                        logger.error(" Intelligent generation failed, using fallback")
                        first_scene_data = script_analysis['scenes'][0]
                        scene_desc = first_scene_data.get('description', str(first_scene_data)) if isinstance(first_scene_data, dict) else str(first_scene_data)
                        image_prompt = f"Cinematic {project.genre or 'film'} opening scene: {project.logline or project.synopsis[:200]}"
                    
                    logger.info(f"Final image prompt ({len(image_prompt)} chars):")
                    logger.debug(f"{image_prompt}")
                    logger.debug(f"---")
                    
                    # Create panel with pending status first
                    panel = StoryboardPanel(
                        scene_id=first_scene.scene_id,
                        panel_number=1,
                        image_prompt=image_prompt,
                        style_reference=project.genre or 'cinematic',
                        status='generating',
                        shot_type='establishing'
                    )
                    db.session.add(panel)
                    db.session.flush()  # Get panel_id
                    
                    # Immediately generate the actual image
                    logger.debug(f"Generating actual image with AI...")
                    generated_image = image_service.generate_image(
                        prompt=image_prompt,
                        negative_prompt="blurry, bad quality, distorted, watermark, low resolution"
                    )
                    
                    if generated_image:
                        panel.generated_image_url = generated_image
                        panel.status = 'completed'
                        panel.generation_timestamp = db.func.now()
                        panel.ai_model_used = 'Gemini Imagen 4'
                        logger.info(f"Image generated and saved successfully!")
                        
                        # Log image generation
                        image_log = AIProcessingLog(
                            project_id=project_id,
                            user_id=user_id,
                            operation_type='storyboard_image_generation',
                            input_data={'prompt': image_prompt, 'logline': project.logline, 'synopsis': project.synopsis},
                            output_data={'status': 'completed', 'has_image': True},
                            ai_model='Gemini Imagen 4',
                            status='completed'
                        )
                        db.session.add(image_log)
                    else:
                        panel.status = 'failed'
                        logger.error(f"Image generation failed")
                    
                    panels_created = 1
                    logger.info(f"Created 1 storyboard panel with {'generated image' if generated_image else 'pending image'}")
                    
                except Exception as panel_error:
                    logger.error(f"Error creating/generating storyboard panel: {panel_error}", exc_info=True)
        
        log_activity(project_id, user_id, 'content_generated',
                    f'Generated script with {scenes_created} scenes and {panels_created} storyboard panels')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Content generated successfully',
            'script_version_id': script_version.version_id,
            'scenes_created': scenes_created,
            'panels_created': panels_created
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def format_enhanced_screenplay(title: str, genre: str, logline: str, script_analysis: dict) -> str:
    """Format screenplay with enhanced structure including act breaks, character info, and visual details"""
    
    script = f"# {title}\n\n"
    script += f"**Genre:** {genre}\n"
    script += f"**Logline:** {logline}\n\n"
    
    # Add character section if available
    if script_analysis.get('characters'):
        script += "## CHARACTERS\n\n"
        for char in script_analysis['characters']:
            script += f"### {char.get('name', 'CHARACTER').upper()}\n"
            script += f"**Role:** {char.get('role', 'Supporting').capitalize()}\n"
            if char.get('description'):
                script += f"**Description:** {char['description']}\n"
            if char.get('motivation'):
                script += f"**Motivation:** {char['motivation']}\n"
            if char.get('arc'):
                script += f"**Arc:** {char['arc']}\n"
            script += "\\n"
    
    # Add synopsis
    script += f"## SYNOPSIS\n\n{script_analysis.get('synopsis', '')}\n\n"
    
    # Add themes and tone
    if script_analysis.get('themes'):
        script += f"**Themes:** {', '.join(script_analysis['themes'])}\n"
    if script_analysis.get('tone'):
        script += f"**Tone:** {script_analysis['tone']}\n"
    if script_analysis.get('pacing'):
        script += f"**Pacing:** {script_analysis['pacing']}\n"
    script += "\\n"
    
    # Add screenplay with act breaks
    script += "## SCREENPLAY\n\n"
    
    current_act = None
    for i, scene in enumerate(script_analysis.get('scenes', []), 1):
        if not isinstance(scene, dict):
            script += f"### SCENE {i}\n{scene}\n\n"
            continue
        
        # Add act break if entering new act
        scene_act = scene.get('act', 1)
        if scene_act != current_act:
            if scene_act == 1:
                script += "═══════════════════════════════════════════════════════════════\n"
                script += "ACT I - SETUP\n"
                script += "═══════════════════════════════════════════════════════════════\n\n"
            elif scene_act == 2:
                script += "\\n═══════════════════════════════════════════════════════════════\n"
                script += "ACT II - CONFRONTATION\n"
                script += "═══════════════════════════════════════════════════════════════\n\n"
            elif scene_act == 3:
                script += "\\n═══════════════════════════════════════════════════════════════\n"
                script += "ACT III - RESOLUTION\n"
                script += "═══════════════════════════════════════════════════════════════\n\n"
            current_act = scene_act
        
        # Scene number and story beat
        scene_num = scene.get('scene_number', i)
        script += f"### SCENE {scene_num}"
        if scene.get('story_beat'):
            script += f" - [{scene['story_beat']}]"
        script += "\\n\\n"
        
        # Scene heading
        script += f"**{scene.get('heading', 'INT. LOCATION - DAY')}**\n\n"
        
        # Production details section
        script += "```\n"
        script += f"MOOD: {scene.get('mood', 'Neutral')}\n"
        script += f"LIGHTING: {scene.get('lighting', 'Natural lighting')}\n"
        script += f"CAMERA: {scene.get('camera_notes', 'Medium shot')}\n"
        if scene.get('sound_design'):
            script += f"SOUND: {scene['sound_design']}\n"
        script += "```\n\n"
        
        # Scene description/action
        if scene.get('description'):
            script += f"{scene['description']}\n\n"
        
        if scene.get('action') and scene.get('action') != scene.get('description'):
            script += f"{scene['action']}\n\n"
        
        # Dialogue
        if scene.get('dialogue'):
            for dialogue_line in scene['dialogue']:
                if isinstance(dialogue_line, dict):
                    character = dialogue_line.get('character', 'CHARACTER').upper()
                    script += f"**{character}**"
                    
                    # Add parenthetical if exists
                    if dialogue_line.get('parenthetical'):
                        script += f"\\n*({dialogue_line['parenthetical']})*"
                    
                    script += f"\\n{dialogue_line.get('line', '')}\n\n"
                else:
                    script += f"{dialogue_line}\n\n"
        
        # Scene transition
        transition = scene.get('transition', 'CUT TO:')
        script += f"*{transition}*\n\n"
    
    script += "\\n═══════════════════════════════════════════════════════════════\n"
    script += "THE END\n"
    script += "═══════════════════════════════════════════════════════════════\n"
    
    return script


