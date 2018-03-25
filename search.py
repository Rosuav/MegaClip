import sys
import megaclip

def search(video, *search_terms):
	info = megaclip.get_video_info(video, verbose=True)

	for msg in info["comments"]:
		for findme in search_terms:
			if findme in msg["message"]["body"]: break
		else:
			continue # Not found? Don't display it.
		secs = int(msg["content_offset_seconds"])
		tm = "[%d:%02d:%02d]" % (secs // 3600, (secs // 60) % 60, secs % 60)
		name = msg["commenter"]["display_name"]
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
