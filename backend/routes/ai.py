"""
AI Processing Routes
Handles AI operations, logs, and analytics
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, AIProcessingLog, UsageAnalytics
from utils.helpers import paginate_query
from datetime import datetime, timedelta

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/project/<int:project_id>/logs', methods=['GET'])
@jwt_required()
def get_ai_logs(project_id):
    """Get AI processing logs for project"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    operation_type = request.args.get('operation_type')
    
    query = AIProcessingLog.query.filter_by(project_id=project_id)
    
    if operation_type:
        query = query.filter_by(operation_type=operation_type)
    
    query = query.order_by(AIProcessingLog.created_at.desc())
    
    result = paginate_query(query, page, per_page)
    
    return jsonify({
        'logs': [log.to_dict() for log in result['items']],
        'pagination': result['pagination']
    }), 200


@ai_bp.route('/analytics/usage', methods=['GET'])
@jwt_required()
def get_usage_analytics():
    """Get user usage analytics"""
    user_id = int(get_jwt_identity())
    days = request.args.get('days', 30, type=int)
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    analytics = UsageAnalytics.query.filter(
        UsageAnalytics.user_id == user_id,
        UsageAnalytics.created_at >= since_date
    ).all()
    
    # Aggregate by event type
    event_counts = {}
    for event in analytics:
        event_type = event.event_type
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    return jsonify({
        'period_days': days,
        'total_events': len(analytics),
        'event_counts': event_counts,
        'recent_events': [a.to_dict() for a in analytics[:10]]
    }), 200


@ai_bp.route('/analytics/track', methods=['POST'])
@jwt_required()
def track_event():
    """Track analytics event"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'event_type' not in data:
        return jsonify({'error': 'event_type is required'}), 400
    
    analytics = UsageAnalytics(
        user_id=user_id,
        event_type=data['event_type'],
        event_data=data.get('event_data'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    db.session.add(analytics)
    db.session.commit()
    
    return jsonify({'message': 'Event tracked'}), 201


@ai_bp.route('/analytics/project/<int:project_id>/summary', methods=['GET'])
@jwt_required()
def get_project_ai_summary(project_id):
    """Get AI usage summary for project"""
    
    # Count operations by type
    from sqlalchemy import func
    operation_counts = db.session.query(
        AIProcessingLog.operation_type,
        func.count(AIProcessingLog.log_id).label('count')
    ).filter_by(project_id=project_id).group_by(AIProcessingLog.operation_type).all()
    
    # Calculate total tokens and cost
    total_stats = db.session.query(
        func.sum(AIProcessingLog.tokens_used).label('total_tokens'),
        func.sum(AIProcessingLog.cost_estimate).label('total_cost'),
        func.avg(AIProcessingLog.processing_time_ms).label('avg_time')
    ).filter_by(project_id=project_id).first()
    
    return jsonify({
        'operations': {op: count for op, count in operation_counts},
        'total_tokens_used': int(total_stats.total_tokens or 0),
        'total_cost_estimate': float(total_stats.total_cost or 0),
        'average_processing_time_ms': int(total_stats.avg_time or 0)
    }), 200
