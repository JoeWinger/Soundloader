import soundcloud, sys, os, requests, subprocess
from mutagen.id3 import ID3, APIC, _util
from mutagen.mp3 import EasyMP3

CLIENT_ID = 'a3dd183a357fcff9a6943c0d65664087'

file_name = ""
track_title = ""
track_genre = ""
track_artist = ""
track_art_url = ""

def downloadSong(song_url):
	global file_name
	global track_title
	global track_genre
	global track_artist
	global track_art_url

	client = soundcloud.Client(client_id=CLIENT_ID)
	track = client.get('/resolve', url=song_url)
	
	file_name = track.title + ".mp3"
	track_title = track.title
	track_genre = track.genre
	track_artist = track.user["username"]
	track_art_url = track.artwork_url

	print("Downloading '%s'..." % track_title)
	FNULL = open(os.devnull, 'w')
	subprocess.run('ffmpeg -i %s "%s"' % (track.stream_url + '?client_id=' + CLIENT_ID, file_name), stdout=FNULL, stderr=subprocess.STDOUT)
	print("Download complete!")

def setMetadata(f_name, title, artist, genre):
	print("Setting metadata...")
	audio = EasyMP3(f_name)
	audio['title'] = title
	audio['artist'] = artist
	audio['genre'] = genre
	audio.save()
	
def setAlbumArt(f_name, album_art):
	print("Fetching album art...")
	img = requests.get(album_art, stream=True)  # Gets album art from url
	img = img.raw

	audio = EasyMP3(f_name, ID3=ID3)

	try:
		audio.add_tags()
	except _util.error:
		pass

	print("Encoding album art...")
	audio.tags.add(
		APIC(
			encoding=3,  # UTF-8
			mime='image/jpeg',
			type=3,  # 3 is for album art
			desc='Cover',
			data=img.read()  # Reads and adds album art
		)
	)
	audio.save(v2_version=3)


if(not sys.argv[len(sys.argv)-1] == '-d'):
	song = downloadSong(sys.argv[1])
	setMetadata(file_name, track_title, track_artist, track_genre)
	setAlbumArt(file_name, track_art_url)
	print("Done! File saved as '%s'" % file_name)