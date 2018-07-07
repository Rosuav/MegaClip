import sys
import os
import megaclip
import collections

GRANULARITY = 60 # Average 
for fn in sorted(os.listdir("cache")):
	info = megaclip.get_video_info(fn.replace(".json", ""), cache_only=True)
	if info["metadata"]["channel"]["name"] != "devicat": continue
	print("\t" + info["metadata"]["created_at"] + "\t" + info["metadata"]["_id"])
	length = info["metadata"]["length"]
	humanmsgs = botmsgs = 0
	spammiest = collections.Counter()
	for msg in info["comments"]:
		if msg["commenter"]["name"] == "cutiecakebot":
			botmsgs += 1
		else:
			humanmsgs += 1
		spammiest[msg["commenter"]["display_name"]] += 1
		pos = int(msg["content_offset_seconds"]) // GRANULARITY
		# TODO: Calculate minute-by-minute granularity
	print("Humans:", humanmsgs/length)
	print("CCB:   ", botmsgs/length)
	for name, count in spammiest.most_common(10):
		print("\t" + name, count/length)
