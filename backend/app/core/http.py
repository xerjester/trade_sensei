# ตัวช่วยสร้าง JSON Response มาตรฐานสำหรับ API (Response Helpers)
from flask import jsonify


# ส่งคืน JSON Response เมื่อการทำงานสำเร็จ พร้อมข้อมูลและ HTTP Status Code
def success_response(data=None, message=None, status=200, **extra):
    payload = {'status': 'success'}
    if message:
        payload['message'] = message
    if data is not None:
        payload['data'] = data
    payload.update(extra)
    return jsonify(payload), status


# ส่งคืน JSON Response เมื่อเกิดข้อผิดพลาด พร้อมข้อความแจ้งเตือนและ HTTP Status Code
def error_response(message, status=400, **extra):
    payload = {'status': 'error', 'message': message}
    payload.update(extra)
    return jsonify(payload), status
