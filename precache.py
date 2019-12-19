# Cache all the available videos for a channel, allowing other scripts to read
# more chat from the cache.
import urllib.parse
from pprint import pprint
from megaclip import get_video_info
import requests # ImportError? "python3 -m pip install requests"
import keys # ImportError? Look at keys_sample.py and follow the instructions.

def cache_all(channel):
	if set(channel) - set("0123456789"):
		# There are non-digits in the channel name - it's a login, not a user ID.
		# It's a lot more efficient to look up UIDs first if you have multiple or
		# are going to do this more than once, but this way, at least it'll work.
		r = requests.get("https://api.twitch.tv/helix/users", params={"login": channel},
			headers={"Client-ID": keys.client_id, "Accept": "application/vnd.twitchtv.v5+json"})
		r.raise_for_status()
		channel = r.json()["data"][0]["id"]
		print("Next time, it'd be faster to precache", channel)
	url = "https://api.twitch.tv/kraken/channels/%s/videos?broadcast_type=archive&limit=100" % channel
	while url:
		r = requests.get(url, headers={"Client-ID": keys.client_id, "Accept": "application/vnd.twitchtv.v5+json"})
		r.raise_for_status()
		data = r.json()
		if not data["videos"]: break # End of list
		for video in data["videos"]:
			print("Ensuring cache of video", video["_id"][1:])
			get_video_info(video["_id"][1:], verbose=True)
		url = data.get("_links", {}).get("next")

if __name__ == "__main__":
	import sys
	if len(sys.argv) < 2:
		print("USAGE: python3 precache.py channel [channel [channel...]]")
	for channel in sys.argv[1:]:
		cache_all(channel)
