
import pprint
import sys

import spotipy.util as util


if __name__ == "__main__":
    if len(sys.argv) > 3:
        user_id = sys.argv[1]
        candidates_uri = sys.argv[2]
        candidates = sys.argv[3:]
    else:
        print "Usage: %s user_id playlist_id track_id ..." % (sys.argv[0],)
        sys.exit()

    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(user_id, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        while candidates:
            end = min(100, len(candidates))
            results = sp.user_playlist_add_tracks(user_id, candidates_uri, candidates[:end])
            candidates = candidates[end:]
            print (results)
    else:
        print ("Can't get token for", user_id)
