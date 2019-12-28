import librosa
import os
import random

import numpy as np
import pandas as pd

import src.vinyl.db_manager as crates

features_dir = 'data/librosa_features'


def extract_features(file, features_dict):
    global features_dir
    
    y, sr = librosa.load(file)
    features = {}
    
    for f in features_dict.keys():
        song_id = os.path.split(file)[-1].split('.')[0]
        filepath = os.path.join(features_dir, f.__name__, song_id + '.npy')
        if os.path.isfile(filepath):
            features[f.__name__] = np.load(filepath)
        else:
            featargs = features_dict[f]
            feature_data = f(y, sr, **featargs)
            np.save(filepath, feature_data)
            features[f.__name__] = feature_data
    
    return features


def collect_features(song_ids, features_dict):
    features = {}
    for song_id in song_ids:
        filepath = crates.get_preview_mp3(song_id)
        if not filepath:
            continue
        feats = extract_features(filepath, features_dict)
        if feats:
            features[song_id] = feats
    
    song_ids = [x for x in song_ids if features.get(x)]
    
    return song_ids, features
    

def prep_audio_features_dataset(song_ids, features):
    n_features = 0
    feats = features[song_ids[0]]
    for k in feats.keys():
        n_features += feats[k].shape[0]
    ts_length = feats[k].shape[1]
    
    data = np.zeros((len(song_ids), ts_length, n_features), dtype=np.float64)
    
    return data


def fill_audio_features_dataset(song_ids, features, data):
    ts_length = data.shape[1]
    for i, song_id in enumerate(song_ids):
        ts = min(ts_length, features[song_id]['mfcc'].shape[1])
        j0 = 0
        for k in features[song_id].keys():
            vals = features[song_id][k].T[0:ts, :]
            j1 = j0 + vals.shape[1]
            data[i, :ts, j0:j1] = vals
            j0 = j1
    return data


def build_dataset(song_ids, features_dict):
    song_ids, features = collect_features(song_ids, features_dict)
    data = prep_audio_features_dataset(song_ids, features)
    data = fill_audio_features_dataset(song_ids, features, data)
            
    return song_ids, data