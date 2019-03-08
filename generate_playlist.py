# This program was created to build playlists for me, that didn't include songs
    # that I already listen to (have saved). Similar to the daily mixes, this
    # program will bunch songs together by genre.

import spotipy
import spotipy.util as util
import json
import random

client_id = '6ee5977e1f83455180575e4b754f4048'
client_secret = '8193de873e1444229508d5964936c028'
redirect_uri = 'https://dummy.com/'

url = 'https://accounts.spotify.com/authorize'
scope = 'user-library-read user-top-read playlist-modify-public user-follow-read'
username = '' #enter username here

token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

sp = spotipy.Spotify(auth=token)

class spotipyFix(spotipy.Spotify):
     def current_user_saved_tracks_contains(self, tracks=None):
        """ Check if one or more tracks is already saved in
            the current Spotify user’s “Your Music” library.
            Parameters:
                - tracks - a list of track URIs, URLs or IDs
        """
        tlist = []
        if tracks is not None:
            tlist = [self._get_id('track', t) for t in tracks]
        return self._get('me/tracks/contains?ids=' + ','.join(tlist))

def authenticate():
    print("Connecting to Spotify...")
    x = spotipy.Spotify(auth=token)
    return x

# def getReccommendations(sp, artist_uri):
#     print('Getting artist reccommendations...')

def getTopArtists():
    auth = authenticate()
    topArtists = []
    topArtistURI = []
    ranges = ['short_term', 'medium_term', 'long_term']
    print('Getting your top artists...')
    for rang in ranges:
        all_data = auth.current_user_top_artists(limit=25, time_range= rang)
        data = all_data['items']
        for artist in data:
            if artist['name'] not in topArtists:
                topArtists.append(artist['name'])
                topArtistURI.append(artist['uri'])
    # print(json.dumps(topArtists + topArtistURI, indent = 2))
    return topArtistURI

def getTopArtistTracks(topArtistURI, sp):
    topArtistTracks = []
    print('Aggregating your top artists\' tracks...')
    for artist in topArtistURI:
        top_tracks_all_data = sp.artist_top_tracks(artist)
        top_tracks = top_tracks_all_data['tracks']
        for track in top_tracks:
            # a lot of music with features has a song posted from each artist, may not need as track uri's are most likely unique
            if track['uri'] not in topArtistTracks:
                topArtistTracks.append(track['uri'])
    # for each in topArtistTracks[:10]:
    #     print(each)
    return topArtistTracks

def generateTopArtistUnsavedList(track_list):
    topArtistUnsavedList = []
    for track in track_list:
        x = sp.current_user_saved_tracks_contains(tracks=track)
        if not x:
            topArtistUnsavedList.append(track)
        return topArtistUnsavedList  

def create_playlist(sp, selected_tracks):
    user = sp.current_user()
    user_id = user['id']
    playlist_name = 'Project playlist'

    print('Creating playlist...')
    playlist = sp.user_playlist_create(user_id, playlist_name)
    playlist_id = playlist['id']
    
    track_list = generateTopArtistUnsavedList(selected_tracks)
    random.shuffle(track_list)
    print('Adding songs...')
    sp.user_playlist_add_tracks(user_id, playlist_id, track_list[0:100])

top = getTopArtists()

# uri = ['spotify:track:3Ol2xnObFdKV9pmRD2t9x8']
# checkAgainstSavedTracks(uri)


selected_tracks = getTopArtistTracks(top, sp)
create_playlist(sp, selected_tracks)

# def function that finds genre reccommendations based off an artist's genre
#   recommendation_genre_seeds()
#   Get a list of genres available for the recommendations function.

# def function that creates reccommendations based off an artist
    # recommendations(seed_artists=None, seed_genres=None, seed_tracks=None, limit=20, country=None, **kwargs)
    # Get a list of recommended tracks for one to five seeds.

    # Parameters:
    # seed_artists - a list of artist IDs, URIs or URLs
    # seed_tracks - a list of artist IDs, URIs or URLs
    # seed_genres - a list of genre names. Available genres for recommendations can be found by calling recommendation_genre_seeds
    # country - An ISO 3166-1 alpha-2 country code. If provided, all results will be playable in this country.
    # limit - The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 100
    # min/max/target_<attribute> - For the tuneable track attributes listed in the documentation, these values provide filters and targeting on results.

# user_playlist_create(user, name, public=True, description='')
# Creates a playlist for a user

# Parameters:
# user - the id of the user
# name - the name of the playlist
# public - is the created playlist public
# description - the description of the playlist

# user_playlist_add_tracks(user, playlist_id, tracks, position=None)
# Adds tracks to a playlist

# Parameters:
# user - the id of the user
# playlist_id - the id of the playlist
# tracks - a list of track URIs, URLs or IDs
# position - the position to add the tracks
