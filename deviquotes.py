# Search the cache for all quotes from DeviCat and list them
import os
import re
import json
import collections
from pprint import pprint
import megaclip

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

CACHE_FILE = "../devicatoutlet.github.io/_quotes.json"
try:
	with open(CACHE_FILE) as f: cache = json.load(f)
except (FileNotFoundError, json.decoder.JSONDecodeError): cache = {}
quotes = cache.get("quotes", []); loadedquotes = list(quotes)
def cache_end(video):
	# If we haven't added/changed any quotes, don't bother updating the markers
	if quotes == loadedquotes: return
	# If we've already saved back once, don't update the cache-end tag
	if "saved" in cache: del cache["saved"]
	else: cache["cached_until"] = video
	cache["quotes"] = quotes
	with open(CACHE_FILE, "w") as f:
		json.dump(cache, f, sort_keys=True, indent=2)
		f.write("\n") # json.dump doesn't put a final newline, but it's tidier with one
	cache["saved"] = 1

popularity = collections.Counter()
def find_quotes(video):
	if "cached_until" in cache and video < cache["cached_until"]: return
	info = megaclip.get_video_info(video, cache_only=True)
	if info["metadata"]["channel"]["name"] not in {"devicat", "devi_cat"}: return
	if info["metadata"]["status"] == "recording":
		# Retain cache of everything up to but not including any
		# incomplete videos. Then next time, load that cache and skip
		# everything up to but not including the cache marker.
		# Note that the popularity stats are not cached. Keeping the
		# cache file and discarding the actual chat logs will reset
		# all quotes to zero and restart the popularity contest.
		cache_end(video)
	print("Scanning video %s (%s)..." % (video, info["metadata"]["status"]))
	for msg in info["comments"]:
		if msg["commenter"]["name"] not in ("cutiecakebot", "candicat"): continue
		m = re.match("#([0-9]+): (.*)$", msg["message"]["body"])
		if not m: continue
		idx = int(m.group(1))
		if not idx: raise ValueError("Something wrong in the data for this line: %r" % msg["message"]["body"])
		quotes.extend([None] * (idx - len(quotes) + 1))
		quotes[idx] = m.group(2) # If a quote changes, retain the most recent version
		popularity[idx] += 1

for fn in sorted(os.listdir("cache")):
	find_quotes(fn.replace(".json", ""))
cache_end(fn.replace(".json", "") + "+") # If we haven't halted the cache, keep everything, and start scanning AFTER the last vid.

assert quotes[0] is None # There should be no quote numbered 0
assert quotes[-1] is not None #  ... and we should have slots only for what we use

most_quoted = collections.Counter()
name_fold = {} # Map case-folded names to the first seen form; whatever we first see, we keep.
name_fold["devi_cat"] = "DeviCat" # Fold some names together to gather renamed people
name_fold["ciriion"] = "Ciri_Ion"
for Erin in "derppicklejar dearpicklejar pickle pickledeggrin picklewash mydearestpickle mydearpotato".split():
	name_fold[Erin] = "Erin (various)"
missing = []

def save_quotes(quotes, filename, desc):
	with open("../devicatoutlet.github.io/%s.md" % filename, "w") as f:
		print("""# Twitch Quotes

<!-- This file is generated by deviquotes.py from the MegaClip project, and
should not be edited manually. -->
<style>img {display: inline-block;} li {line-height: 35px;}</style>

During live streams, funny things that people say can be recorded for posterity
by the faithful bot and the mod team. %s

""" % desc, file=f)
		for idx, quote in enumerate(quotes):
			if quote is None:
				if not idx: continue # Ignore the shim
				missing.append(idx)
				print("* <missing quote %d, ask CandiCat for it please>" % idx, file=f)
			else:
				print("* %d: %s" % (idx, convert_emotes(quote)), file=f)
				m = re.search(r"-(\w+) \([0-9][0-9]-[A-Z][a-z][a-z]-[0-9][0-9]\)$", quote)
				if m: most_quoted[name_fold.setdefault(m.group(1).casefold(), m.group(1))] += 1
		if missing: print("\nThis list is missing %d quotes, plus any that have been recently added." % len(missing), file=f)
		else: print("\nThere may be quotes newer than these that have yet to be collected.\n", file=f)

save_quotes(quotes, "quotes", """So far, %d quotes have been recorded. To
see them in chat, ask the bot for a quote with the command `!quote N` for some
number N.""" % (len(quotes) - 1))

if "--all" in sys.argv:
	for filename, desc in cache["sections"].items():
		save_quotes(cache[filename], filename, desc + """, %d quotes were recorded. They cannot
be seen in chat, but have been archived here with their original numbers.""" % (len(cache[filename]) - 1))

if missing: print("Missing quote(s) %s" % ", ".join(map(str, missing)))
else: print("Last quote:\n%d: %s" % (len(quotes)-1, quotes[-1]))
print()
# print("Top ten quotes:")
# for idx, freq in popularity.most_common(10):
	# print("%d: %s" % (idx, quotes[idx]))
# print()
# print("Most quoted people:")
# for name, freq in most_quoted.most_common(10):
	# print("%d: %s" % (freq, name))
