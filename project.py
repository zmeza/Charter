import pygn
import sys
from sklearn import linear_model
import json
from sklearn.feature_extraction import DictVectorizer


def main():
	# f = open('new_metadata.json', 'rw')
	# data = json.load(f)
	# f.close()
	#data = getGraceNoteMetadata("Adele", "Hello")
	#json.dump(data, open('newest.json', 'w'), indent=4)
	#return

	fin = open('data/train_paths.json', 'r')
	train_data_json = json.load(fin) # is a map


	train_paths_file = open('data/train_paths.json', 'r')
	train_data = json.load(train_paths_file) # is a map

	song_paths_test_file = open('data/test_paths.json', 'r')
	test_data_json = json.load(song_paths_test_file) # is a map




	fetchGraceNoteData = False
	if fetchGraceNoteData:
		gracenote_metadata = {}
	else:
		metadata_file = open('new_metadata.json')
		gracenote_metadata = json.load(metadata_file)
		metadata_file.close()


	# for elem in gracenote_metadata:
	# 	print elem
	# raw_input()

	# new_metadata = {}
	# for elem in gracenote_metadata['tracks']:
	# 	song = elem["track_title"]
	# 	artist = elem["album_artist_name"]
	# 	new_metadata[song + " ::: " + artist] = elem
	# json.dump(new_metadata, open('new_metadata.json', 'w'))

	for n in range(1, 11):
		all_n_runs = []
		n_runs_next_output = []
		match = 0
		total = 0
		for elem in train_data:
			total += 1
			song, artist = elem.split(":::")
			if fetchGraceNoteData:
				track_metadata = getGraceNoteMetadata(artist, song)
			else:
				if elem in gracenote_metadata:
					track_metadata = gracenote_metadata[elem]
				else:
					continue
			song_name = track_metadata['track_title']
			artist_name = track_metadata['album_artist_name']

			if fetchGraceNoteData and artist.strip() == artist_name.strip() and song.strip() == song_name.strip():
				gracenote_metadata[elem] = track_metadata
				match += 1
				print str(match) + "/" + str(total)

			moods_map = {}
			if "mood" in gracenote_metadata[elem]:
				moods = gracenote_metadata[elem]["mood"]
				for key in moods:
					moods_map[moods[key]["TEXT"]] = 1

			positions_list = []
			for i,x in enumerate(train_data[elem]):
				positions_list.append(int(x[2]))

			if len(positions_list) >= n:
				for i in range(len(positions_list)-n):
					features = dict(moods_map)
					for j in range(i, i+n):
						features['pos'+str(j-i)] = positions_list[j]
					all_n_runs.append(features)
					n_runs_next_output.append(positions_list[i+n])	
		#print "Matched: " + str(match) + "/" + str(total)

		if fetchGraceNoteData:
			json.dump(gracenote_metadata, open('gracenote_metadata.json', 'w'))

		v = DictVectorizer(sparse=True)
		all_n_runs_vectorized = v.fit_transform(all_n_runs)

		clf = linear_model.Ridge(alpha=0.1)
		clf.fit(all_n_runs_vectorized, n_runs_next_output)

		total_error = 0
		num = 0
		for elem in test_data_json:
			song, artist = elem.split(":::")
			positions_list = []
			for x in test_data_json[elem]:
				positions_list.append(int(x[2]))
			if elem in gracenote_metadata:
				track_metadata = gracenote_metadata[elem]
			else:
				continue

			feature_names = v.get_feature_names()
			feature_list = [0] * len(feature_names)
			if "mood" in gracenote_metadata[elem]:
				moods = gracenote_metadata[elem]["mood"]
				for key in moods:
					if moods[key]["TEXT"] in feature_names:
						feature_list[feature_names.index(moods[key]["TEXT"])] = 1


			if len(positions_list) >= n:
				for i in range(len(positions_list)-n):
					for j in range(i, i+n):
						key = 'pos' + str(j-i)
						index = feature_names.index(key)
						feature_list[index] = positions_list[j]
					num += 1
					prediction = clf.predict([feature_list])[0]
					actual = positions_list[i+n]
					print "Predicted: ", prediction
					print "Actual value: ", actual
					print "\n"
					difference = abs(prediction - actual)
					total_error += difference
		print "Average error for runs of length %d = %f" % (n, float(total_error)/num)







def getGraceNoteMetadata(artist, song):
	clientID = '2122781398-E1CD26B308E4A8C61E4DDED49E9D1D60' # Enter your Client ID here
	userID = pygn.register(clientID)
	metadata = pygn.search(clientID=clientID, userID=userID, artist=artist, track=song)
	'''for elem in metadata:
		if str(metadata[elem]) != '':
			print 'Field = ' + elem
			print '\t' + str(metadata[elem])
			print "\n"
	'''
	return metadata
	# f = open('output.xml', 'w')
	# f.write(str(metadata))




if __name__ == '__main__':
	main()
