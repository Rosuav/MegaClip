# Create a clip-like playable page that can exceed Twitch's 60-second limitation
import json
import hashlib
import html
import os
import subprocess
import sys
from pprint import pprint

CACHE_DIR = "cache"

# See if we have the chat already downloaded and in cache
def get_video_info(video, verbose=False):
	# TODO: If "video" is actually a channel name (eg "devicat"), fetch the video ID of the
	# current or most-recent stream.
	os.makedirs(CACHE_DIR, exist_ok=True)
	try:
		with open(CACHE_DIR + "/%s.json" % video) as f:
			info = json.load(f)
			if {"metadata", "comments"} - info.keys():
				raise ValueError("Cached JSON file is corrupt")
			if info["metadata"]["status"] == "recording":
				# TODO: Allow the cache to be used if and only if it's sufficient
				# For now, if the video was still being recorded last time, we'll
				# just ignore the cache.
				raise FileNotFoundError # Pretend that the file actually didn't exist
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
	# Grab the playlist URL and cache that too. TODO: Can we construct this from info
	# we already have? Or at least partially, thus saving 1-2 HTTP queries?
	info["m3u8"] = subprocess.check_output(["youtube-dl", "-g", "https://www.twitch.tv/videos/%s" % video]).decode("utf-8").strip()
	with open(CACHE_DIR + "/%s.json" % video, "w") as f:
		json.dump(info, f)
	if verbose:
		print("Downloading chat - complete", file=sys.stderr)
	return info

def hms_to_sec(hms):
	"""Parse "1:23:45" into an integer seconds"""
	parts = str(hms).split(":")
	sec = 0
	for part in parts: sec = (sec * 60) + int(part)
	return sec

def download_video(video, start, length, clipname, chat_only=False):
	start = hms_to_sec(start)
	length = hms_to_sec(length)
	# Length or end time? Assume that clips are likely to be short.
	# If you take a long clip from near the beginning of the VOD,
	# provide the end time, not the length.
	if length > start: length -= start
	info = get_video_info(video, verbose=True)

	title = info["metadata"]["title"]
	print("Video title:", title)

	with open(clipname + ".html", "w") as f:
		print("""<!DOCTYPE HTML>
<html>
<head>
<meta charset="utf-8">
<style>
main {display: flex;}
section {display: flex; flex-direction: column;}
video {
	max-width: 75vw;
}
#chat {
	flex-basis: 0px;
	flex-grow: 1;
	overflow-y: auto;
	font-family: sans-serif;
}
#chat li {
	list-style: none;
	margin-top: 10px;
}
.hidden {
	display: none !important;
}
#morechat {
	display: block;
	position: relative;
	bottom: 0;
	background: lightgrey;
	margin: auto;
}
#chat span:first-child {font-weight: bold;}
</style>
""", file=f)
		print("""</head>
<body>
<h4>%s</h4>
<main>
<section><video src="%s.mkv" controls autoplay></video></section>
<section><ul id="chat">
""" % (title, clipname), file=f)

		for msg in info["comments"]:
			pos = msg["content_offset_seconds"] - start
			if pos < 0 or pos > length: continue
			color = msg["message"].get("user_color")
			if not color:
				# Twitch randomizes, but stably. For simplicity, we don't randomize, we hash.
				# By creating a three-digit colour (eg "#fb4"), we restrict the potential
				# colors to a reasonable set; taking six digits would create a lot of subtle
				# shades and wouldn't really improve things.
				color = "#" + hashlib.md5(msg["commenter"]["name"].encode("utf-8")).hexdigest()[:3]
			line = '<li class=hidden data-time="%.3f"><span style="color: %s">%s</span>' % (
				pos, color,
				msg["commenter"]["display_name"],
			)
			if msg["message"]["is_action"]:
				line += '<span style="color: %s"> ' % color
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
<a id=morechat class=hidden href="#">More chat below...</a>
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
	const t = this.currentTime;
	document.querySelectorAll("li").forEach(li => li.classList.toggle("hidden", (t < +li.dataset.time) || (t-120 > +li.dataset.time)))

	//Convenience part 2: do the scrolling
	if (autoscroll) chat.scrollTop = chat.scrollHeight;
	document.querySelector("#morechat").classList.toggle("hidden", autoscroll);
}

document.querySelector("#morechat").onclick = function(ev) {
	ev.preventDefault();
	const chat = document.querySelector("#chat");
	chat.scrollTop = chat.scrollHeight;
	this.classList.add("hidden");
}
</script>
</body>
</html>
""", file=f)
	# Download the actual video
	if not chat_only:
		subprocess.check_call(["ffmpeg", "-y", "-ss", str(start), "-i", info["m3u8"],
			"-t", str(length), "-c", "copy", clipname + ".mkv"])

def main(args):
	import argparse
	parser = argparse.ArgumentParser(description="Download clips from Twitch")
	parser.add_argument("video", help="video ID or (TODO) URL")
	parser.add_argument("start", help="start time [hh:]mm:ss")
	parser.add_argument("length", help="length in seconds or end time as [hh:]mm:ss")
	parser.add_argument("clipname", help="destination file name")
	parser.add_argument("--chat-only", action="store_true", help="skip the downloading of the actual video")
	args = parser.parse_args(args)
	download_video(**vars(args))

if __name__ == "__main__":
	main(sys.argv[1:])
