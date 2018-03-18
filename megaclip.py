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
}
#chat li {
	list-style: none;
	margin-top: 5px;
	display: none;
}
#chat span {font-weight: bold;}
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
		print(msg["commenter"]["display_name"] + ": " + msg["message"]["body"])
		# TODO: Display differently if msg["message"]["is_action"] (ie if it's a /me)
		line = '<li class="p%d"><span style="color: %s">%s</span>: ' % (
			pos,
			msg["message"].get("user_color", "black"), # TODO: Randomize stably, the way Twitch does
			msg["commenter"]["display_name"],
		)
		for frag in msg["message"]["fragments"]:
			if "emoticon" in frag:
				line += '<img src="https://static-cdn.jtvnw.net/emoticons/v1/%s/1.0" title="%s">' % (
					frag["emoticon"]["emoticon_id"],
					frag.get("text", ""), # it's probably always there but be safe anyway
				)
			else:
				line += html.escape(frag["text"])
		line += "</li>"
		print(line, file=f)
	"""
<li class="p3"><span style="color: #B22222">the_frozen666</span>: this is a first time improv everyone!</li>
<li class="p34"><span style="color: #14A503">dylanplaysguitar</span>: doing great Hannah, glad to see you singing ! <img src="https://static-cdn.jtvnw.net/emoticons/v1/1/1.0" title=":)"> you are awesome Hannah!!! <img src="https://static-cdn.jtvnw.net/emoticons/v1/1/1.0" title=":)"></li>
	"""
	print("""
</ul>
</section>
</main>
<div id="time"></div>
<script>
document.querySelector("video").volume = 0.25; //hack

document.querySelector("video").ontimeupdate = function() {
	document.querySelector("#time").innerHTML = this.currentTime;
	const t = this.currentTime|0;
	const chat = document.querySelector("#chat");
	chat.className = "tm" + (this.currentTime|0);
	chat.scrollTop = chat.scrollHeight;
}
</script>
</body>
</html>
""", file=f)
