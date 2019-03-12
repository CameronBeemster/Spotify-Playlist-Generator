# This program was created to build playlists for me, that didn't include songs
    # that I already listen to (have saved). Similar to the daily mixes, this
    # program will bunch songs together by genre.

import spotipy
import spotipy.util as util
import json
import random
import datetime
import urllib.request
import base64

client_id = '6ee5977e1f83455180575e4b754f4048'
client_secret = '8193de873e1444229508d5964936c028'
redirect_uri = 'https://dummy.com/'

url = 'https://accounts.spotify.com/authorize'
scope = 'user-library-read user-top-read playlist-modify-public user-follow-read ugc-image-upload'
username = '' #enter username here

print("Connecting to Spotify...")
token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
sp = spotipy.Spotify(auth=token)

def getTopArtists():
    topArtists = []
    topArtistsURI = []
    ranges = ['short_term', 'medium_term', 'long_term']
    print('Getting your top artists...')
    for rang in ranges:
        all_data = sp.current_user_top_artists(limit=10, time_range= rang)
        data = all_data['items']
        for artist in data:
            if artist['name'] not in topArtists:
                topArtists.append(artist['name'])
                topArtistsURI.append(artist['uri'])
    return topArtistsURI

def userPromptArtist(topArtistsURI):
    artist_names = {}
    for artist in topArtistsURI:
        artist_data = sp.artist(artist)
        name = artist_data['name']
        print(name)
        name = name.lower()
        artist_names[name] = artist_data['uri']
    correct_artist = False
    while correct_artist == False:
        selection = input('\nSelect an Artist: ')
        if selection.lower() not in artist_names:
            print('\nPlease select an artist from the list...')
        else:
            correct_artist = True
    uri = artist_names[selection]
    selectedArtist = {selection:uri}
    return selectedArtist

def getRelatedArtists(selected_artist):
    for artist, key in selected_artist.items():
        artistKey = key
    related = sp.artist_related_artists(artistKey)['artists']
    relatedArtistURI = {}
    for artist in related:
        uri = artist['uri']
        name = artist['name']
        relatedArtistURI[name] = uri
    print(json.dumps(relatedArtistURI, indent=2))
    return relatedArtistURI

def getTopTracks(artistList):
    topArtistTracks = {}
    print('Aggregating your top artists\' tracks...')
    for artist, key in artistList.items():
        top_tracks_all_data = sp.artist_top_tracks(key)
        top_tracks = top_tracks_all_data['tracks']
        count = 0
        for track in top_tracks:
            uri = track['uri']
            name = track['name']
            is_saved = sp.current_user_saved_tracks_contains(tracks=uri[14:])
            if is_saved == [False] and count < 4: #type is a list object
                print(name + " by " + artist + " has been added!")
                topArtistTracks[name] = uri
                count += 1
            elif is_saved == [False] and count >= 4: #only 100 songs can be added to the playlist, so to allow for all related artist to be included 4 songs is the limit 
                break
            else:
                print("You already have " + name + " by " + artist + " saved!")            
    print(json.dumps(topArtistTracks, indent=2))
    print(len(topArtistTracks))
    return topArtistTracks

def getArtistArtwork(artist): 
    for key in artist.values():
        artistKey = key
    artistData = sp.artist(artistKey)
    image = artistData['images'][0]
    artworkURL = image['url']
    print(artworkURL)
    urllib.request.urlretrieve(artworkURL, "playlistArtwork.jpeg")
    with open("playlistArtwork.jpeg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string

def createPlaylist(selected_tracks, artist): #, encodedPhoto):
    user = sp.current_user()
    userID = user['id']

    for key in artist.values():
        artistKey = key

    artistData = sp.artist(artistKey)
    name = artistData['name']

    playlistName = name + " playlist (created on " + str(datetime.datetime.today().strftime('%m/%d')) + ")"

    print('Creating playlist...')
    playlist = sp.user_playlist_create(userID, playlistName)
    playlistID = playlist['id']

    track_list = []
    for song in selected_tracks.values():
        track_list.append(song)
    
    random.shuffle(track_list)
    print('Adding songs...\n')
    sp.user_playlist_add_tracks(userID, playlistID, track_list)
    # print('Adding flair...\n')
    # sp.changePlaylistArtwork(userID, playlistID, encodedPhoto)
    
top = getTopArtists()
selectedArtist = userPromptArtist(top)
# topArtistArtwork = getArtistArtwork(selectedArtist)
related = getRelatedArtists(selectedArtist)

playlistTracks = getTopTracks(selectedArtist)
relatedTracks = getTopTracks(related)
playlistTracks.update(relatedTracks)

createPlaylist(playlistTracks, selectedArtist) #, topArtistArtwork)