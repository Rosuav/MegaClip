import collections
import sys
import megaclip

def search(video, cache_only=False):
	if video == "cache":
		import os
		for fn in os.listdir("cache"):
			search(fn.replace(".json", ""), cache_only=True)
		return

	# People are identified by ID, but we keep the display name for, well, display
	people = collections.defaultdict(collections.Counter)
	displaynames = {}
	info = megaclip.get_video_info(video, verbose=True, cache_only=cache_only)

	for msg in info["comments"]:
		# msg["message"]["user_badges"] may be of use, but it is possible for bots
		# to receive gift subs...
		people[msg["commenter"]["_id"]][msg["message"]["body"]] += 1
		displaynames[msg["commenter"]["_id"]] = msg["commenter"]["display_name"]

	one_tricks = ""

	for person, msgs in people.items():
		if len(msgs) > 10: continue # If you've said more than ten unique things, you're fine
		if len(msgs) == 1:
			# You've only ever said one thing. Dubious.
			msg, count = msgs.most_common()[0]
			if count == 1: continue # But you only said it once. No big deal.
			one_tricks += "%s => %d of %s\n" % (displaynames[person], count, msg)
			continue
		# If the total unique characters in what you've said is high enough,
		# you're probably fine. This is tricky to put a boundary on.
		totlength = sum(len(msg) for msg in msgs)
		totmsgs = sum(msgs.values())
		# Saying the same things more frequently is bad (low score), but
		# saying just one thing and vanishing is okay. Long messages are
		# usually from humans, so that's a good thing.
		score = (len(msgs) / totmsgs) * totlength
		if score > 20: continue
		print("\nLimited vocabulary:", score, displaynames[person])
		for msg, count in msgs.most_common():
			print("\t%d => %s" % (count, msg))

	if one_tricks:
		print("\n**************************\n")
		print(one_tricks)
		print("**************************\n")

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("USAGE: python3 %s videoid" % sys.argv[0])
		print("Searches that video's chat for people who only type a few commands")
	else:
		search(*sys.argv[1:])
