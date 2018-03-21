# Create a clip-like playable page that can exceed Twitch's 60-second limitation
import json
import hashlib
import html
import os
import subprocess
import sys
from pprint import pprint

CACHE_DIR = "cache"
# TODO: Parse sys.argv
VIDEO_ID = 239937840
START = 1*3600 + 48*60 + 50
LENGTH = 225
CLIP_NAME = "TVC plays for DeviCat"

# See if we have the chat already downloaded and in cache
def get_video_info(video, verbose=False):
	os.makedirs(CACHE_DIR, exist_ok=True)
	try:
		with open(CACHE_DIR + "/%s.json" % video) as f:
			info = json.load(f)
			if {"metadata", "comments"} - info.keys():
				raise ValueError("Cached JSON file is corrupt")
			return info
	except FileNotFoundError:
		# It's not downloaded. Let's make it.
		pass # De-chain any exceptions
	import requests # ImportError? "python3 -m pip install requests"
	import keys # ImportError? Look at keys_sample.py and follow the instructions.
	params = {"client_id": keys.client_id}
	r = requests.get("https://api.twitch.tv/v5/videos/%s" % video, params)
	r.raise_for_status()
	metadata = r.json()
	# Grab the playlist URL and cache that too. TODO: Can we construct this from info
	# we already have? Or at least partially, thus saving 1-2 HTTP queries?
	metadata["m3u8"] = subprocess.check_output(["youtube-dl", "-g", "https://www.twitch.tv/videos/%s" % video]).decode("utf-8").strip()
	comments = []
	params["cursor"] = ""
	while params["cursor"] is not None:
		r = requests.get("https://api.twitch.tv/v5/videos/%s/comments" % video, params)
		r.raise_for_status()
		data = r.json()
		comments.extend(data["comments"])
		if verbose and data["comments"]:
			pos = int(100 * data["comments"][-1]["content_offset_seconds"] / metadata["length"])
			print("Downloading chat [%02d%%]..." % pos, end="\r", file=sys.stderr)
		params["cursor"] = data.get("_next")
	info = {"comments": comments, "metadata": metadata}
	with open(CACHE_DIR + "/%s.json" % video, "w") as f:
		json.dump(info, f)
	if verbose:
		print("Downloading chat - complete", file=sys.stderr)
	return info

info = get_video_info(VIDEO_ID, verbose=True)

title = info["metadata"]["title"]
print("Video title:", title)

with open(CLIP_NAME + ".html", "w") as f:
	print("""<!DOCTYPE HTML>
<html>
<head>
<meta charset="utf-8">
<style>
main {display: flex;}
section {display: flex; flex-direction: column;}
#chat {
	flex-basis: 0px;
	flex-grow: 1;
	overflow-y: auto;
	font-family: sans-serif;
}
#chat li {
	list-style: none;
	margin-top: 10px;
	display: none;
}
#chat span:first-child {font-weight: bold;}
</style>
<style>
""", file=f)
	for t in range(LENGTH+1):
		for p in range(t, min(t+120, LENGTH+1)):
			print("#chat.tm%d li.p%d {display: list-item}" % (p, t), file=f)
	print("""</style>
</head>
<body>
<h4>%s</h4>
<main>
<section><video src="%s.mkv" controls autoplay></video></section>
<section><ul id="chat">
""" % (title, CLIP_NAME), file=f)

	for msg in info["comments"]:
		pos = int(msg["content_offset_seconds"] - START)
		if pos < 0 or pos > LENGTH: continue
		color = msg["message"].get("user_color")
		if not color:
			# Twitch randomizes, but stably. For simplicity, we don't randomize, we hash.
			# By creating a three-digit colour (eg "#fb4"), we restrict the potential
			# colors to a reasonable set; taking six digits would create a lot of subtle
			# shades and wouldn't really improve things.
			color = "#" + hashlib.md5(msg["commenter"]["name"].encode("utf-8")).hexdigest()[:3]
		line = '<li class="p%d"><span style="color: %s">%s</span>' % (
			pos,
			color,
			msg["commenter"]["display_name"],
		)
		if msg["message"]["is_action"]:
			line += '<span style="color: %s">' % color
		else:
			line += ": <span>"

		for frag in msg["message"]["fragments"]:
			if "emoticon" in frag:
				line += '<img src="https://static-cdn.jtvnw.net/emoticons/v1/%s/1.0" title="%s">' % (
					frag["emoticon"]["emoticon_id"],
					frag.get("text", ""), # it's probably always there but be safe anyway
				)
			else:
				line += html.escape(frag["text"])
		line += "</span></li>"
		print(line, file=f)
	print("""
</ul>
</section>
</main>
<div id="time"></div>
<script>
document.querySelector("video").volume = 0.25; //hack

document.querySelector("video").ontimeupdate = function() {
	//Debugging: show the time as a number
	document.querySelector("#time").innerHTML = this.currentTime;

	//Convenience: Scroll chat to the bottom only if we're already at the bottom
	const chat = document.querySelector("#chat");
	const autoscroll = chat.scrollTop >= chat.scrollHeight - chat.clientHeight;

	//Magic: Display chat that's within the last two minutes
	const t = this.currentTime|0;
	chat.className = "tm" + (this.currentTime|0);

	//Convenience part 2: do the scrolling
	if (autoscroll) chat.scrollTop = chat.scrollHeight;
}
</script>
</body>
</html>
""", file=f)
