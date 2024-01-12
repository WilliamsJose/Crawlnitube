from flask import Flask
from flask_cors import CORS
from api.routes.anime_routes import anime_bp
from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/anime/*": {"origins": "*"}})

app.register_blueprint(anime_bp)

if __name__ == '__main__':
    app.run(debug=True, port=4000, host='0.0.0.0')
