from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///playlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    playlists = db.relationship('PlaylistSong', back_populates='song')

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    songs = db.relationship('PlaylistSong', back_populates='playlist')

class PlaylistSong(db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)
    position = db.Column(db.Integer)
    playlist = db.relationship('Playlist', back_populates='songs')
    song = db.relationship('Song', back_populates='playlists')

# Create database tables
with app.app_context():
    db.create_all()

# Song endpoints
@app.route('/songs', methods=['POST'])
def create_song():
    data = request.json
    new_song = Song(
        title=data['title'],
        artist=data['artist'],
        genre=data.get('genre', '')
    )
    db.session.add(new_song)
    db.session.commit()
    return jsonify({'message': 'Song created successfully', 'id': new_song.id}), 201

@app.route('/songs/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    song = Song.query.get_or_404(song_id)
    data = request.json
    song.title = data.get('title', song.title)
    song.artist = data.get('artist', song.artist)
    song.genre = data.get('genre', song.genre)
    db.session.commit()
    return jsonify({'message': 'Song updated successfully'})

@app.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    return jsonify({'message': 'Song deleted successfully'})

@app.route('/songs', methods=['GET'])
def search_songs():
    query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'title')
    
    # Base query
    songs = Song.query
    
    # Search functionality
    if query:
        songs = songs.filter(
            db.or_(
                Song.title.ilike(f'%{query}%'),
                Song.artist.ilike(f'%{query}%'),
                Song.genre.ilike(f'%{query}%')
            )
        )
    
    # Sorting
    if sort_by == 'title':
        songs = songs.order_by(Song.title)
    elif sort_by == 'artist':
        songs = songs.order_by(Song.artist)
    elif sort_by == 'genre':
        songs = songs.order_by(Song.genre)
    
    songs = songs.all()
    return jsonify([{
        'id': song.id,
        'title': song.title,
        'artist': song.artist,
        'genre': song.genre
    } for song in songs])

# Playlist endpoints
@app.route('/playlists', methods=['POST'])
def create_playlist():
    data = request.json
    new_playlist = Playlist(name=data['name'])
    db.session.add(new_playlist)
    db.session.commit()
    return jsonify({'message': 'Playlist created successfully', 'id': new_playlist.id}), 201

@app.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    songs = [{
        'id': ps.song.id,
        'title': ps.song.title,
        'artist': ps.song.artist,
        'genre': ps.song.genre,
        'position': ps.position
    } for ps in sorted(playlist.songs, key=lambda x: x.position or float('inf'))]
    
    return jsonify({
        'id': playlist.id,
        'name': playlist.name,
        'songs': songs
    })

@app.route('/playlists/<int:playlist_id>', methods=['PUT'])
def update_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    data = request.json
    playlist.name = data.get('name', playlist.name)
    db.session.commit()
    return jsonify({'message': 'Playlist updated successfully'})

@app.route('/playlists/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    return jsonify({'message': 'Playlist deleted successfully'})

# Playlist management endpoints
@app.route('/playlists/<int:playlist_id>/songs', methods=['POST'])
def add_song_to_playlist(playlist_id):
    data = request.json
    song_id = data['song_id']
    position = data.get('position')
    
    # Verify playlist and song exist
    playlist = Playlist.query.get_or_404(playlist_id)
    song = Song.query.get_or_404(song_id)
    
    # Check if song is already in playlist
    existing = PlaylistSong.query.filter_by(
        playlist_id=playlist_id,
        song_id=song_id
    ).first()
    
    if existing:
        return jsonify({'message': 'Song already in playlist'}), 400
    
    # If position is not specified, add to end
    if position is None:
        max_position = db.session.query(db.func.max(PlaylistSong.position))\
            .filter_by(playlist_id=playlist_id).scalar()
        position = (max_position or 0) + 1
    
    playlist_song = PlaylistSong(
        playlist_id=playlist_id,
        song_id=song_id,
        position=position
    )
    db.session.add(playlist_song)
    db.session.commit()
    
    return jsonify({'message': 'Song added to playlist successfully'})

@app.route('/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
def remove_song_from_playlist(playlist_id, song_id):
    playlist_song = PlaylistSong.query.filter_by(
        playlist_id=playlist_id,
        song_id=song_id
    ).first_or_404()
    
    db.session.delete(playlist_song)
    db.session.commit()
    return jsonify({'message': 'Song removed from playlist successfully'})

@app.route('/playlists/<int:playlist_id>/sort', methods=['POST'])
def sort_playlist(playlist_id):
    data = request.json
    sort_by = data.get('sort_by', 'title')
    
    playlist = Playlist.query.get_or_404(playlist_id)
    
    # Get all playlist songs with their song information
    playlist_songs = playlist.songs
    
    # Sort based on criteria
    if sort_by == 'title':
        sorted_songs = sorted(playlist_songs, key=lambda ps: ps.song.title)
    elif sort_by == 'artist':
        sorted_songs = sorted(playlist_songs, key=lambda ps: ps.song.artist)
    elif sort_by == 'genre':
        sorted_songs = sorted(playlist_songs, key=lambda ps: ps.song.genre)
    else:
        return jsonify({'message': 'Invalid sort criteria'}), 400
    
    # Update positions
    for i, ps in enumerate(sorted_songs, 1):
        ps.position = i
    
    db.session.commit()
    return jsonify({'message': f'Playlist sorted by {sort_by} successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
