from flask import Blueprint, render_template, jsonify, current_app
from flask_login import login_required, current_user
from . import db
from .models import Notification

notifications = Blueprint('notifications', __name__)

@notifications.route('/notifications')
@login_required
def list():
    """显示用户的所有通知"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).all()
    
    return render_template('notifications.html', notifications=notifications)

@notifications.route('/notifications/<int:id>/read', methods=['POST'])
@login_required
def mark_as_read(id):
    """将单个通知标记为已读"""
    notification = Notification.query.get_or_404(id)
    
    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作此通知'}), 403
        
    try:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f'标记通知已读失败: {str(e)}')
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'}), 500

@notifications.route('/notifications/mark_all_read', methods=['POST'])
@login_required
def mark_all_read():
    """将所有通知标记为已读"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).update({'is_read': True})
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f'标记所有通知已读失败: {str(e)}')
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'}), 500

@notifications.route('/notifications/count')
@login_required
def get_unread_count():
    """获取未读通知数量"""
    try:
        count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        current_app.logger.error(f'获取未读通知数量失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': '获取未读通知数量失败'
        }), 500