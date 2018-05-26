import sys
import os
import megaclip

# Populate the cache as required
for video in sys.argv[1:]:
	megaclip.get_video_info(video, verbose=True)

for fn in sorted(os.listdir("cache")):
	info = megaclip.get_video_info(fn.replace(".json", ""), cache_only=True)
	if info["metadata"]["channel"]["name"] != "devicat": continue
	print("\t" + info["metadata"]["created_at"] + "\t" + info["metadata"]["_id"])
	msgs = 0; song = songpos = None
	for msg in info["comments"]:
		if msg["commenter"]["name"] != "cutiecakebot":
			msgs += 1
			continue
		txt = msg["message"]["body"]
		if not txt.startswith("Currently playing: "):
			# Note that CCB's messages don't get counted, but
			# people talking to her will be. So the spam commands
			# get counted once, not twice.
			# msgs += 1
			continue
		nextpos = int(msg["content_offset_seconds"])
		if song is not None and msgs > 0:
			msg_rate = 60 * msgs / (nextpos - songpos)
			if msgs > 100 and msg_rate > 30:
				print("%.2f\t%d\t%s" % (msg_rate, msgs, song))
		msgs = 0
		song = txt[len("Currently playing: "):]
		songpos = nextpos