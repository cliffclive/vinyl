import os
import random
import requests
import time

def download_preview_mp3(url, filepath):
    if os.path.isfile(filepath):
        return
    time.sleep(random.random()/2)
    preview = requests.get(url, allow_redirects=True)
    open(filepath, 'wb').write(preview.content)


def sample_non_zouk_songs(n_songs, genres, metadata_dir):
    # Keep track of URLs for song samples, so we can download them if they're missing.
    sample_urls = {}

    non_zouk_genres = random.choices(genres, k=30)
    non_zouk_songs = []
    for genre in non_zouk_genres:
        metadata_path = os.path.join(metadata_dir, genre)
        metadata = pd.read_csv(metadata_path, sep='\t').dropna()
        non_zouk_songs.extend(metadata['id'].tolist())

        for i in metadata.index:
            sample_urls[metadata['id'][i]] = metadata['preview_mp3'][i]

    non_zouk_songs = random.choices(non_zouk_songs, k=n_songs)

    return non_zouk_songs, sample_urls


