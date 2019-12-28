import os, json, time, random, requests


# Globals
sample_mp3_dir = 'data/mp3s'
metadata_dir = "data/song_metadata"
playlists_dir = "data/genre_playlists"
features_dir = "data/librosa_features"


def get_tags(track):
    '''
    Parse metadata for a spotify track
    From a user_playlist json file, a track can be found via:
        user_playlist['tracks']['items'][i]
    '''
    tags =  {
        'id': track['id'],
        'album': track['album']['name'],
        'track': track['track_number'],
        'title': track['name'],
        'artist': track['artists'][0]['name'],
        'duration': int(track['duration_ms']/1000),
        'preview_mp3': track['preview_url'],
        'is_explicit': track['explicit'],
        'isrc_number': track['external_ids'].get('isrc', ''),
        'release_date': track['album']['release_date']
    }
    if track['album']['images']:
        tags['cover_art_url'] = track['album']['images'][0]['url']
    return tags


def read_save_tags(track):
    global metadata_dir
    track_tags = get_tags(track) 
    if not track_tags['id']:
        return None
    song_file = os.path.join(metadata_dir, track_tags['id']) + '.json'
    if not os.path.isfile(song_file):
        with open(song_file, 'w') as file:
            json.dump(track_tags, file)
    return track_tags['id']
    


def download_playlist_songs(client, user_name, playlist_name, playlist_uri):
    global playlists_dir

    results = client.user_playlist(user_name, playlist_uri, fields="tracks,next")
    tracks = results['tracks']
    
    track_ids = []
    
    # loop through track batches, 
    #   write metadata to json
    #     append id to track_ids,
    #       get next batch of tracks
    while True:
        for item in tracks['items']:
            if item['track']:
                track_id = read_save_tags(item['track'])
                if track_id:
                    track_ids.append(track_id)
        if tracks['next']:
            tracks = client.next(tracks)
        else:
            break        

    playlist_file = os.path.join(playlists_dir, playlist_name) + '.txt'
    with open(playlist_file, 'w') as file:
        file.writelines('\n'.join(track_ids))

    return track_ids


def get_playlist_songs(playlist_name):
    global playlists_dir
    playlist_file = os.path.join(playlists_dir, playlist_name) + '.txt'
    with open(playlist_file, 'r') as file:
        songs = [x.strip() for x in file.readlines()]
    return songs


def load_song_metadata(song_id):
    global metadata_dir
    # TODO: download song metadata if not found locally
    md_path = os.path.join(metadata_dir, song_id) + '.json'
    with open(md_path, 'r') as f:
        metadata = json.load(f)
    return metadata


def get_preview_mp3(song_id):
    global sample_mp3_dir    
    preview_url = load_song_metadata(song_id).get('preview_mp3')
    if not preview_url:
        return ''
    filepath = os.path.join(sample_mp3_dir, song_id + ".mp3")
    if not os.path.isfile(filepath):
        time.sleep(random.random()/2)
        content = requests.get(preview_url, allow_redirects=True).content
        open(filepath, 'wb').write(content)
    return filepath


def sample_other_songs(n_songs, n_genres=30, skip_genres=[]):
    global playlists_dir
    playlists = os.listdir(playlists_dir)
    for genre in skip_genres:
        playlists.remove(genre + ".txt")

    other_genres = random.choices(playlists, k=n_genres)
    other_songs = []
    for playlist in other_genres:
        playlist_path = os.path.join(playlists_dir, playlist)
        with open(playlist_path, 'r') as f:
            playlist_songs = [x.strip() for x in f.readlines()]
            playlist_songs = [x for x in playlist_songs if load_song_metadata(x).get('preview_mp3')]
        other_songs.extend(playlist_songs)

    other_songs = random.choices(other_songs, k=n_songs)
    return other_songs


def get_playlist_songs(playlist_name):
    global playlists_dir
    playlist_file = os.path.join(playlists_dir, playlist_name) + '.txt'
    with open(playlist_file, 'r') as file:
        songs = [x.strip() for x in file.readlines()]
    return songs


def load_song_metadata(song_id):
    global metadata_dir
    md_path = os.path.join(metadata_dir, song_id) + '.json'
    with open(md_path, 'r') as f:
        metadata = json.load(f)
    return metadata