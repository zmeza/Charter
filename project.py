import pygn
import sys
from sklearn import linear_model
import json

def main():
	song_paths_train_file = open('data/song_paths_train.json', 'r')
	train_data_json = json.load(song_paths_train_file) # is a map

	song_paths_test_file = open('data/song_paths_test.json', 'r')
	test_data_json = json.load(song_paths_test_file) # is a map

	all_three_runs = []
	three_runs_next_output = []


	fetchGraceNoteData = False
	if fetchGraceNoteData:
		metadata_file = open('metadata.json')
	else:
		metadata_file = open('new_metadata.json')
	gracenote_metadata = json.load(metadata_file)
	metadata_file.close()


	
	for elem in train_data_json:
		if elem not in gracenote_metadata:
			print "not there"
			print elem
			print "\n\n"
	raw_input()

	# for elem in gracenote_metadata:
	# 	print elem
	# raw_input()

	# new_metadata = {}
	# for elem in gracenote_metadata['tracks']:
	# 	song = elem["track_title"]
	# 	artist = elem["album_artist_name"]
	# 	new_metadata[song + " ::: " + artist] = elem
	# json.dump(new_metadata, open('new_metadata.json', 'w'))


	for elem in train_data_json:
		song, artist = elem.split(":::")
		if fetchGraceNoteData:
			track_metadata = getGraceNoteMetadata(artist, song)
		else:
			if elem in gracenote_metadata:
				track_metadata = gracenote_metadata[elem]
			else:
				print song, artist
				print "not there...\n"
				continue
		song_name = track_metadata['track_title']
		artist_name = track_metadata['album_artist_name']

		tempo = track_metadata['tempo']
		print song_name
		print artist_name
		print tempo
		raw_input()

		if fetchGraceNoteData and artist.strip() == artist_name.strip() and song.strip() == song_name.strip():
			gracenote_metadata['tracks'].append(track_metadata)

		positions_list = []
		for x in train_data_json[elem]:
			positions_list.append(int(x[u'position']))
		if len(positions_list) >= 4:
			for i in range(len(positions_list)-4):
				all_three_runs.append([positions_list[i], positions_list[i+1], positions_list[i+2], ])
				three_runs_next_output.append(positions_list[i+3])	
	print "finished lol"
	raw_input()

	if fetchGraceNoteData:
		json.dump(metadata, open('metadata.json', 'w'))

	clf = linear_model.Ridge(alpha=0.4)
	clf.fit(all_three_runs, three_runs_next_output)

	total_error = 0
	num = 0
	for elem in test_data_json:
		song, artist = elem.split(":::")
		positions_list = []
		for x in test_data_json[elem]:
			positions_list.append(int(x[u'position']))
		if len(positions_list) >= 4:
			for i in range(len(positions_list)-4):
				num += 1
				prediction = clf.predict([[positions_list[i], positions_list[i+1], positions_list[i+2]]])[0]
				actual = positions_list[i+3]
				print "Predicted: ", prediction
				print "Actual value: ", actual
				print "\n"
				difference = abs(prediction - actual)
				total_error += difference
	print "Average error", (float(total_error)/num)







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