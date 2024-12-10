# Playlist Management API

This is a Flask-based API for managing playlists and songs. It provides comprehensive functionality for creating, updating, and managing both songs and playlists.

## Features

- CRUD operations for songs and playlists
- Add/remove songs from playlists
- Search songs by title, artist, or genre
- Sort playlists by various criteria
- SQLite database for persistent storage

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

## API Endpoints

### Song Endpoints

- `POST /songs` - Create a new song
- `PUT /songs/<id>` - Update a song
- `DELETE /songs/<id>` - Delete a song
- `GET /songs?query=<search_term>&sort_by=<criteria>` - Search/sort songs

### Playlist Endpoints

- `POST /playlists` - Create a new playlist
- `GET /playlists/<id>` - Get playlist details
- `PUT /playlists/<id>` - Update playlist
- `DELETE /playlists/<id>` - Delete playlist

### Playlist Management

- `POST /playlists/<id>/songs` - Add song to playlist
- `DELETE /playlists/<id>/songs/<song_id>` - Remove song from playlist
- `POST /playlists/<id>/sort` - Sort playlist songs

## Data Structures Used

- SQLAlchemy ORM for database management
- Lists and dictionaries for data manipulation
- Efficient sorting algorithms for playlist management

## Example Usage

1. Create a song:
```bash
curl -X POST http://localhost:3000/songs -H "Content-Type: application/json" -d '{"title":"My Song","artist":"Artist Name","genre":"Pop"}'
```

2. Create a playlist:
```bash
curl -X POST http://localhost:3000/playlists -H "Content-Type: application/json" -d '{"name":"My Playlist"}'
```

3. Add song to playlist:
```bash
curl -X POST http://localhost:3000/playlists/1/songs -H "Content-Type: application/json" -d '{"song_id":1}'
```
