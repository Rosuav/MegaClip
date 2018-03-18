# Create a clip-like playable page that can exceed Twitch's 60-second limitation
import json
import html
import os
from pprint import pprint

# TODO: Parse sys.argv
CHAT_DIR = "../Twitch-Chat-Downloader/output"
VIDEO_ID = 239937840
START = 1*3600 + 48*60 + 50
LENGTH = 225
CLIP_NAME = "TVC plays for DeviCat"

chat = None
for channel in os.listdir(CHAT_DIR):
	# There's a subdir with the channel name. Since we don't know the channel, search.
	try:
		with open(os.path.join(CHAT_DIR, channel, "v%d.json" % VIDEO_ID)) as f:
			chat = json.load(f)
		break
	except FileNotFoundError:
		pass
if chat is None:
	# TODO: Automatically download it:
	# cd ../Twitch-Chat-Downloader; python3 app.py -v {VIDEO_ID} -f json
	print("Chat not found, please go get it")
	sys.exit(1)

title = chat["video"]["title"]
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
	for t in range(LENGTH):
		for p in range(t, min(t+120, LENGTH)):
			print("#chat.tm%d li.p%d {display: list-item}" % (p, t), file=f)
	print("""</style>
</head>
<body>
<h4>%s</h4>
<main>
<section><video src="%s.mkv" controls autoplay></video></section>
<section id="heightlimit"><ul id="chat">
""" % (title, CLIP_NAME), file=f)

	for msg in chat["comments"]:
		pos = int(msg["content_offset_seconds"] - START)
		if pos < 0 or pos > LENGTH: continue
		line = '<li class="p%d"><span style="color: %s">%s</span>' % (
			pos,
			msg["message"].get("user_color", "black"), # TODO: Randomize stably, the way Twitch does
			msg["commenter"]["display_name"],
		)
		if msg["message"]["is_action"]:
			line += '<span style="color: %s">' % msg["message"].get("user_color", "black")
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
