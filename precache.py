# Cache all the available videos for a channel, allowing other scripts to read
# more chat from the cache.
import urllib.parse
from pprint import pprint
from megaclip import get_video_info
import requests # ImportError? "python3 -m pip install requests"
import keys # ImportError? Look at keys_sample.py and follow the instructions.

def cache_all(channel):
	url = "https://api.twitch.tv/kraken/channels/%s/videos?broadcast_type=archive&limit=100" % urllib.parse.quote(channel, "")
	while url:
		r = requests.get(url, headers={"Authorization": "OAuth " + keys.oauth})
		r.raise_for_status()
		data = r.json()
		if not data["videos"]: break # End of list
		for video in data["videos"]:
			print("Ensuring cache of video", video["_id"][1:])
			get_video_info(video["_id"][1:], verbose=True)
		url = data["_links"]["next"]

if __name__ == "__main__":
	import sys
	if len(sys.argv) < 2:
		print("USAGE: python3 cacheall.py channel [channel [channel...]]")
	for channel in sys.argv[1:]:
		cache_all(channel)
