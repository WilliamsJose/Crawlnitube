from flask import Blueprint, jsonify, request, Response
from api.services.anime_service import get_recent_episodes, search_anime, stream_episode_by_id, find_anime_info

anime_bp = Blueprint('anime_bp', __name__, url_prefix='/anime')

@anime_bp.route('/latest', methods=['GET'])
def recent_episodes():
    page = int(request.args.get('page', 1))
    results = get_recent_episodes(page)
    return jsonify(results)

@anime_bp.route('/search', methods=['GET'])
def search():
    name = request.args.get('name')
    results = search_anime(name)
    return jsonify(results)
  
@anime_bp.route('/info', methods=['GET'])
def find_anime():
    name = request.args.get('name')
    results = find_anime_info(name)
    return jsonify(results)
  
@anime_bp.route('/stream', methods=['GET'])
def stream_episode():
  id  = request.args.get('id')
  return Response(stream_episode_by_id(id), mimetype="video/mp4")
