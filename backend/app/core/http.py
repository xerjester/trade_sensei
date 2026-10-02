"""Shared JSON response helpers for routers."""
from flask import jsonify


def success_response(data=None, message=None, status=200, **extra):
    payload = {'status': 'success'}
    if message:
        payload['message'] = message
    if data is not None:
        payload['data'] = data
    payload.update(extra)
    return jsonify(payload), status


def error_response(message, status=400, **extra):
    payload = {'status': 'error', 'message': message}
    payload.update(extra)
    return jsonify(payload), status
