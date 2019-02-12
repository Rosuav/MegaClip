# Search the cache for all quotes from DeviCat and list them
import os
import re
import collections
from pprint import pprint
import megaclip
quotes = []

try:
	import sys
	sys.path.append("../shed")
	import emotify
except ImportError:
	# Can't find emotify? No probs, just don't convert them.
	def convert_emotes(msg): return msg
else:
	# Activate BTTV and FFZ emotes from DeviCat's channel
	emotify.load_bttv("devicat")
	emotify.load_ffz("54212603")
	from emotify import convert_emotes # More convenient to have just the function

popularity = collections.Counter()
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
		quotes[idx] = m.group(2) # If a quote changes, retain the most recent version
		popularity[idx] += 1

for fn in sorted(os.listdir("cache")):
	find_quotes(fn.replace(".json", ""))

assert quotes[0] is None # There should be no quote numbered 0
assert quotes[-1] is not None #  ... and we should have slots only for what we use

with open("../devicatoutlet.github.io/quotes.md", "w") as f:
	print("""# Twitch Quotes

<!-- This file is generated by deviquotes.py from the MegaClip project, and
should not be edited manually. -->
<style>img {display: inline-block;} li {line-height: 35px;}</style>

During live streams, funny things that people say can be recorded for posterity
by CutieCakeBot and the mod team. So far, %d quotes have been recorded. Most of
them are listed below; to see the others, ask CutieCakeBot for a quote with the
command `!quote N` for some number N.

""" % (len(quotes)-1), file=f)
	missing = []
	for idx, quote in enumerate(quotes):
		if quote is None:
			if not idx: continue # Ignore the shim
			missing.append(idx)
			print("* <missing quote %d, ask CCB for it please>" % idx, file=f)
		else:
			print("* %d: %s" % (idx, convert_emotes(quote)), file=f)
	if missing: print("\nThis list is missing %d quotes, plus any that have been recently added." % len(missing), file=f)
	else: print("\nThere may be quotes newer than these that have yet to be collected.\n", file=f)

if missing: print("Missing quotes %s" % ", ".join(map(str, missing)))
else: print("Last quote:\n%d: %s" % (len(quotes)-1, quotes[-1]))
print()
print("Top ten quotes:")
for idx, freq in popularity.most_common(10):
	print("%d: %s" % (idx, quotes[idx]))
