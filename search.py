import re
import sys
from collections import Counter
import megaclip

def search(video, *search_terms, cache_only=False, show_header=False):
	if isinstance(video, str):
		# Cache lookup - recurse for every cached entry
		if video.startswith("cache"):
			video = video.casefold()
			import os
			for fn in sorted(os.listdir("cache")):
				info = megaclip.get_video_info(fn.replace(".json", ""), verbose=True, cache_only=True)
				if video in ("cache", "cache:" + info["metadata"]["channel"]["name"]):
					search(info, *search_terms, show_header=True)
			return
		# Otherwise just go fetch, assuming it's some valid identifier (video ID, channel name, etc)
		info = megaclip.get_video_info(video, verbose=True, cache_only=cache_only)
	else:
		info = video

	search_terms = [term.casefold() for term in search_terms]

	status = {}; count = Counter()
	for msg in info["comments"]:
		for findme in search_terms:
			if findme in msg["message"]["body"].casefold(): break
			if findme == msg["commenter"]["name"].casefold(): break
			if (findme == "!quote" and
				msg["commenter"]["name"] == "cutiecakebot" and
				re.match("#[0-9]+: ", msg["message"]["body"])):
					break
			if findme == "!vip":
				badges = {b["_id"]: b for b in msg["message"].get("user_badges", ())}
				badge = "[]"
				if "vip" in badges: badge = "[VIP]"
				elif "moderator" in badges: badge = "[MOD]"
				elif "broadcaster" in badges: badge = "[B/C]"
				who = msg["commenter"]["name"].casefold()
				if badge != status.get(who):
					status[who] = badge
					print(msg["commenter"]["display_name"], badge)
				continue
			if findme == "!active":
				count[msg["commenter"]["display_name"]] += 1
				continue
			if findme.startswith("emote!"):
				for em in msg["message"].get("emoticons", ()):
					name = msg["message"]["body"][em["begin"]:em["end"]+1]
					if (name.startswith(findme.replace("emote!", "")) # eg "emote!2020" will find emotes that start "2020"
							and name not in status):
						print(name, em["_id"])
						status[name] = 1
		else:
			continue # Not found? Don't display it.
		if show_header:
			meta = info["metadata"]
			print()
			print("%s at %s\n%s playing %s - %s" % (meta["url"], meta["created_at"], meta["channel"]["display_name"], meta["game"], meta["title"]))
			show_header = False # First time only
		secs = int(msg["content_offset_seconds"])
		tm = "[%d:%02d:%02d]" % (secs // 3600, (secs // 60) % 60, secs % 60)
		name = msg["commenter"]["display_name"]
		if name.casefold() != msg["commenter"]["name"]:
			# Probably a localized name. Worst case, we show the name twice.
			name += " (%s)" % msg["commenter"]["name"]
		# TODO (maybe): Colorize the name
		if msg["message"]["is_action"]:
			print(tm, name, msg["message"]["body"])
		else:
			print(tm, name + ":", msg["message"]["body"])
	for name, qty in count.most_common(25): # Will do nothing if you're not searching for '!active'
		print("%4d %s" % (qty, name))

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("USAGE: python3 %s videoid search_term [search_term...]" % sys.argv[0])
		print("Searches that video's chat for any of the given words")
	else:
		search(*sys.argv[1:])
