# Search the cache for all quotes from DeviCat and list them
import os
import re
from pprint import pprint
import megaclip
quotes = []

def find_quotes(video):
	info = megaclip.get_video_info(video, cache_only=True)
	if info["metadata"]["channel"]["name"] not in {"devicat", "devi_cat"}: return
	print("Scanning video %s..." % video)
	for msg in info["comments"]:
		if msg["commenter"]["name"] != "cutiecakebot": continue
		m = re.match("#([0-9]+): (.*)$", msg["message"]["body"])
		if not m: continue
		idx = int(m.group(1))
		if not idx: raise ValueError("Something wrong in the data for this line: %r" % msg["message"]["body"])
		quotes.extend([None] * (idx - len(quotes) + 1))
		quotes[idx] = m.group(2)

for fn in os.listdir("cache"):
	find_quotes(fn.replace(".json", ""))
assert quotes[0] is None # There should be no quote numbered 0
assert quotes[-1] is not None #  ... and we should have slots only for what we use
#pprint(quotes)
for idx in 1, 345, 443, 484, len(quotes)-1:
	print(idx, quotes[idx])
print("%d/%d quotes missing" % (sum(x is None for x in quotes)-1, len(quotes)-1))
