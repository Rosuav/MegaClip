import re
import sys
import megaclip

def search(video, *search_terms, cache_only=False):
	if video == "cache":
		import os
		for fn in os.listdir("cache"):
			search(fn.replace(".json", ""), *search_terms, cache_only=True)
		return

	search_terms = [term.casefold() for term in search_terms]
	info = megaclip.get_video_info(video, verbose=True, cache_only=cache_only)

	for msg in info["comments"]:
		for findme in search_terms:
			if findme in msg["message"]["body"].casefold(): break
			if findme == msg["commenter"]["name"].casefold(): break
			if (findme == "!quote" and
				msg["commenter"]["name"] == "cutiecakebot" and
				re.match("#[0-9]+: ", msg["message"]["body"])):
					break
		else:
			continue # Not found? Don't display it.
		# print(video, info["metadata"]["created_at"]); break # To just show which videos have hits
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

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("USAGE: python3 %s videoid search_term [search_term...]" % sys.argv[0])
		print("Searches that video's chat for any of the given words")
	else:
		search(*sys.argv[1:])
