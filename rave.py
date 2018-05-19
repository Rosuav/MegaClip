import sys
import os
import megaclip

for fn in os.listdir("cache"):
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
			continue
		nextpos = int(msg["content_offset_seconds"])
		if song is not None and msgs > 0:
			msg_rate = (nextpos - songpos) / msgs
			if msgs > 100 or msg_rate < 3:
				print("%.2f\t%s" % (60/msg_rate, song))
		msgs = 0
		song = txt[len("Currently playing: "):]
		songpos = nextpos