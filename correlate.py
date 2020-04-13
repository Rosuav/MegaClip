import collections
import itertools
import sys
import megaclip

def search(*videos):
	people = collections.defaultdict(collections.Counter)
	for video in videos:
		info = megaclip.get_video_info(video, verbose=True)
		counts = collections.Counter(msg["commenter"]["display_name"] for msg in info["comments"])
		#print(info["metadata"]["channel"]["display_name"], dict(counts.most_common(5)))
		people[info["metadata"]["channel"]["display_name"]] += counts
	for v1, v2 in itertools.combinations(people, 2):
		common = people[v1] & people[v2]
		if not common: continue
		print("%s/%s: " % (v1, v2))
		for namecount in common.most_common():
			print("\t%s (%d+ messages)" % namecount)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("USAGE: python3 %s video1 video2" % sys.argv[0])
		print("Finds people common to each video")
	else:
		search(*sys.argv[1:])
