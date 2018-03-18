# Create a clip-like playable page that can exceed Twitch's 60-second limitation
import json
import os
from pprint import pprint

# TODO: Parse sys.argv
CHAT_DIR = "../Twitch-Chat-Downloader/output"
VIDEO_ID = 239937840
START = 1*3600 + 48*60 + 50
LENGTH = 225

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
