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
    id = request.args.get('id')
    page = int(request.args.get('page', 1))
    results = find_anime_info(id, page)
    return jsonify(results)
  
@anime_bp.route('/stream', methods=['GET'])
def stream_episode():
  id = request.args.get('id')
  response_generator = stream_episode_by_id(id)
  response = Response(response_generator, mimetype="application/vnd.apple.mpegurl")
#   response = Response(response_generator, mimetype="application/x-mpegURL")
#   response = Response(response_generator, mimetype="video/mp4")
  response.headers.add('Accept-Ranges', 'bytes')
  return response
