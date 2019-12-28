# FUNCTIONS TO GET PLAYLIST METADATA FROM SPOTIFY

import os
import pandas as pd
import spotipy.oauth2 as oauth2
from dotenv import load_dotenv



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


def build_metadata_df(tracks, client):
    #metadata = []
    #for track in tracks['items']:
    #    # read tags from the playlist JSON
    #    metadata.append(get_tags(track['track']))
    metadata = [get_tags(item['track']) for item in tracks['items'] if item['track']]
    metadata_df = pd.DataFrame(metadata).dropna()
    # add more features from the tracks' audio features JSON
    features = client.audio_features(list(metadata_df['id']))
    features_df = pd.DataFrame(features)
    metadata_df = pd.merge(metadata_df, features_df)

    return metadata_df


def download_playlist_metadata(client, user, pid, pname=None):
    # get metadata for playlist 'pname' by 'user'
    results = client.user_playlist(user, pid, fields="tracks,next,name")
    tracks = results['tracks']
    if pname==None:
        pname = results['name'].replace(' ', '_')

    all_dfs = []
    batch_df = build_metadata_df(tracks, client)
    all_dfs.append(batch_df)

    while tracks['next']:
        tracks = client.next(tracks)
        batch_df = build_metadata_df(tracks, client)
        all_dfs.append(batch_df)
    metadata = pd.concat(all_dfs)
    metadata.reset_index(drop=True, inplace=True)

    return metadata


def download_all_genres_metadata(client, genre_playlists, genre_metadata_dir):
    for k,v in genre_playlists.items():
        pname = k
        filepath = os.path.join(genre_metadata_dir, f'{pname}_metadata.tsv')
        if os.path.isfile(filepath):
            continue
        pid = parse_sos_pid(v)
        metadata = download_playlist_metadata('thesoundsofspotify', pid, pname, client)
        metadata.to_csv(filepath, sep='\t', index=False)


def parse_sos_pid(playlists):
    return [x.split('/')[-1] for x in playlists if 'thesoundsofspotify' in x][0]

def generate_token(username):
    """ Generate the token. Please respect these credentials :) """
    load_dotenv('.env')
    
    # Cache for 'username' needs to be clear to load a new token.
    try:
        os.remove(f".cache-{username}")
    except:
        pass

    #scope = 'playlist-modify-public'
    credentials = oauth2.SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"))
    token = credentials.get_access_token()
    return token

