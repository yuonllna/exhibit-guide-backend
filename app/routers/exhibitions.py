from flask import Blueprint, jsonify
from models import Exhibition  # 예시, 프로젝트 모델명에 따라 변경

bp = Blueprint('exhibitions', __name__)

@bp.route('/api/exhibitions', methods=['GET'])
def get_exhibitions():
    exhibition_list = Exhibition.query.all()
    return jsonify([e.to_dict() for e in exhibition_list])
