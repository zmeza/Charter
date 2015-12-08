#!/usr/bin/python -tt

import json
import random


def main():
	years = range(1958, 2016)
	song_peak = {}

	fin = open('data/song_paths.json', 'r')
	fin.seek(13)
	paths_json = json.load(fin)

	ftrain = open('data/train_paths.json', 'w')
	ftrain.seek(0)
	ftrain.truncate()
	ftest = open('data/test_paths.json', 'w')
	ftest.seek(0)
	ftest.truncate()

	test_dict = {}
	train_dict = {}

	for song_key, path in paths_json.iteritems():
		if random.random() >= 0.9:
			test_dict[song_key] = path
		else:
			train_dict[song_key] = path

	print len(paths_json), len(test_dict), len(train_dict)

	ftrain.write(json.dumps(train_dict, indent=4))

	ftest.write(json.dumps(test_dict, indent=4))



if __name__ == '__main__':
	main()