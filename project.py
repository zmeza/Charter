import pygn
import sys
from sklearn import linear_model
import json

var = 'This is just a test to see if this works.'

def main():
	song_paths_train_file = open('data/song_paths_train.json', 'r')
	train_data_json = json.load(song_paths_train_file) # is a map

	song_paths_test_file = open('data/song_paths_test.json', 'r')
	test_data_json = json.load(song_paths_test_file) # is a map

	all_three_runs = []
	three_runs_next_output = []


	total = 0
	for elem in train_data_json:
		song, artist = elem.split(":::")
		print artist
		print song
		metadata = getGraceNoteMetadata(artist, song)
		song_name metadata['track_title']
		artist_name = metadata['album_artist_name']

		if artist.strip() == artist_name.strip() and song.strip() == song_name.strip():
			total+=1
		#print metadata
		raw_input()
		positions_list = []
		for x in train_data_json[elem]:
			positions_list.append(int(x[u'position']))
		if len(positions_list) >= 4:
			for i in range(len(positions_list)-4):
				all_three_runs.append([positions_list[i], positions_list[i+1], positions_list[i+2]])
				three_runs_next_output.append(positions_list[i+3])	
	print total
	raw_input()

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
