from flask import request
from flask_socketio import emit, join_room, leave_room
from app import socketio

active_connections = {}

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    active_connections[request.sid] = {'rooms': []}
    emit('connected', {'status': 'connected', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')
    if request.sid in active_connections:
        del active_connections[request.sid]

@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to job updates"""
    job_id = data.get('job_id')
    if job_id:
        join_room(job_id)
        if request.sid in active_connections:
            active_connections[request.sid]['rooms'].append(job_id)
        print(f'Client {request.sid} subscribed to job {job_id}')
        emit('subscribed', {'job_id': job_id}, room=request.sid)

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Unsubscribe from job updates"""
    job_id = data.get('job_id')
    if job_id:
        leave_room(job_id)
        if request.sid in active_connections and job_id in active_connections[request.sid]['rooms']:
            active_connections[request.sid]['rooms'].remove(job_id)
        print(f'Client {request.sid} unsubscribed from job {job_id}')

def emit_progress(job_id, progress, message):
    """Emit progress update to client"""
    emit('progress_update', {
        'job_id': job_id,
        'progress': progress,
        'message': message
    }, room=job_id)

def emit_complete(job_id, video_url):
    """Emit completion event to client"""
    emit('job_complete', {
        'job_id': job_id,
        'video_url': video_url
    }, room=job_id)

def emit_error(job_id, error_message):
    """Emit error event to client"""
    emit('job_error', {
        'job_id': job_id,
        'error': error_message
    }, room=job_id)

def emit_status(job_id, status):
    """Emit status update to client"""
    emit('job_status', {
        'job_id': job_id,
        'status': status
    }, room=job_id)
