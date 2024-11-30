from flask import Flask, request, jsonify, render_template
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import os

app = Flask(__name__)
api = Api(app)

# YouTube API Configuration
YOUTUBE_API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Video Model
class VideoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"Video(name={self.name}, views={self.views}, likes={self.likes})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'views': self.views,
            'likes': self.likes
        }

# Create database tables
with app.app_context():
    db.create_all()

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        if parsed_url.path[:7] == '/embed/':
            return parsed_url.path.split('/')[2]
        if parsed_url.path[:3] == '/v/':
            return parsed_url.path.split('/')[2]
    return None

def get_video_data(video_id):
    """Fetch video data from YouTube API"""
    try:
        video_response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()

        if not video_response['items']:
            return None

        video_data = video_response['items'][0]
        return {
            'name': video_data['snippet']['title'],
            'views': int(video_data['statistics'].get('viewCount', 0)),
            'likes': int(video_data['statistics'].get('likeCount', 0))
        }
    except Exception as e:
        print(f"Error fetching YouTube data: {str(e)}")
        return None

# Request Parser
video_parser = reqparse.RequestParser()
video_parser.add_argument("name", type=str, help="Name of the video is required", required=True)
video_parser.add_argument("views", type=int, help="Number of views is required", required=True)
video_parser.add_argument("likes", type=int, help="Number of likes is required", required=True)
video_parser.add_argument("youtube_url", type=str, help="YouTube URL to extract data from")

class VideoResource(Resource):
    def get(self, video_id):
        video = VideoModel.query.get(video_id)
        if not video:
            return {'message': 'Video not found'}, HTTPStatus.NOT_FOUND
        return video.to_dict(), HTTPStatus.OK
    
    def put(self, video_id):
        args = video_parser.parse_args()
        
        # Check if YouTube URL is provided
        if 'youtube_url' in args and args['youtube_url']:
            yt_video_id = extract_video_id(args['youtube_url'])
            if yt_video_id:
                video_data = get_video_data(yt_video_id)
                if video_data:
                    args['name'] = video_data['name']
                    args['views'] = video_data['views']
                    args['likes'] = video_data['likes']
        
        video = VideoModel.query.get(video_id)
        if video:
            return {'message': 'Video already exists'}, HTTPStatus.CONFLICT
            
        new_video = VideoModel(
            id=video_id,
            name=args['name'],
            views=args['views'],
            likes=args['likes']
        )
        
        try:
            db.session.add(new_video)
            db.session.commit()
            return new_video.to_dict(), HTTPStatus.CREATED
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating video', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
    
    def delete(self, video_id):
        video = VideoModel.query.get(video_id)
        if not video:
            return {'message': 'Video not found'}, HTTPStatus.NOT_FOUND
            
        try:
            db.session.delete(video)
            db.session.commit()
            return '', HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error deleting video', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    def patch(self, video_id):
        video = VideoModel.query.get(video_id)
        if not video:
            return {'message': 'Video not found'}, HTTPStatus.NOT_FOUND
            
        args = video_parser.parse_args()
        
        try:
            video.name = args['name']
            video.views = args['views']
            video.likes = args['likes']
            db.session.commit()
            return video.to_dict(), HTTPStatus.OK
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error updating video', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

# Register the resource
api.add_resource(VideoResource, "/video/<int:video_id>")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
