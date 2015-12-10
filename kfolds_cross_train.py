#!/usr/bin/python -tt

import pygn
import sys
from sklearn import linear_model
#from sklearn.svm import SVR
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
import scipy
import json

DELIM = ':::'

def main():
	args = sys.argv[1:]
	#window_size = int(args[0])

	fin = open('data/train_paths.json', 'r')
	train_data_json = json.load(fin) # is a map


	all_three_runs = []
	three_runs_next_output = []

	print 'overall: [0, %d]' % (len(train_data_json) - 1)

	num_train = len(train_data_json)
	print num_train

	window_sizes = range(1,11)
	errors_by_window_size = [None] * 10
	for n, window_size in enumerate(window_sizes):
		total_error = 0
		fold_len = num_train / 10
		total_error += hold_out_fold(range(fold_len), train_data_json, 1, window_size)

		for i in range(1, 10):
			if (i < 9):
				total_error += hold_out_fold(range((i) * fold_len, (i + 1) * fold_len), train_data_json, i + 1, window_size)
			else:
				total_error += hold_out_fold(range((i) * fold_len, num_train), train_data_json, i + 1, window_size)
		errors_by_window_size[n] = 'overall error for window size %d: %f' % (window_size, total_error / 10.0)
		#print 'overall error for window size %d: %f' % (window_size, total_error / 10.0)
	for error in errors_by_window_size:
		print error

	# total = 0
	# for elem in train_data_json:
	# 	song, artist = elem.split(":::")
	# 	print artist
	# 	print song
	# 	metadata = getGraceNoteMetadata(artist, song)
	# 	song_name metadata['track_title']
	# 	artist_name = metadata['album_artist_name']

	# 	if artist.strip() == artist_name.strip() and song.strip() == song_name.strip():
	# 		total+=1
	# 	#print metadata
	# 	raw_input()
	# 	positions_list = []
	# 	for x in train_data_json[elem]:
	# 		positions_list.append(int(x[u'position']))
	# 	if len(positions_list) >= 4:
	# 		for i in range(len(positions_list)-4):
	# 			all_three_runs.append([positions_list[i], positions_list[i+1], positions_list[i+2]])
	# 			three_runs_next_output.append(positions_list[i+3])	
	# print total
	# raw_input()

	# clf = linear_model.Ridge(alpha=0.4)
	# clf.fit(all_three_runs, three_runs_next_output)

	# total_error = 0
	# num = 0
	# for elem in test_data_json:
	# 	song, artist = elem.split(":::")
	# 	positions_list = []
	# 	for x in test_data_json[elem]:
	# 		positions_list.append(int(x[u'position']))
	# 	if len(positions_list) >= 4:
	# 		for i in range(len(positions_list)-4):
	# 			num += 1
	# 			prediction = clf.predict([[positions_list[i], positions_list[i+1], positions_list[i+2]]])[0]
	# 			actual = positions_list[i+3]
	# 			print "Predicted: ", prediction
	# 			print "Actual value: ", actual
	# 			print "\n"
	# 			difference = abs(prediction - actual)
	# 			total_error += difference
	# print "Average error", (float(total_error)/num)


def hold_out_fold(hold_out_indices, data_dict, fold_num, window_size):
	song_keys = data_dict.keys()
	held_out = {song_keys[ind] : data_dict[song_keys[ind]] for ind in hold_out_indices}
	train = {song_keys[ind] : data_dict[song_keys[ind]] for ind in range(len(data_dict)) if ind not in hold_out_indices}

	input_features = []
	next_entries = []
	for elem, data in train.iteritems():
		song, artist = elem.split(DELIM)
		if len(data) > window_size:
			first_three = [data[i][2] for i in range(window_size)]
			# first_three = [data[0][2]]
			# for i in range(1, window_size):
			# 	first_three.append(data[i][2] - data[i - 1][2])
			first_three.append(data[0][0] - 1958)
			first_three.append(data[0][1])

			input_features.append(first_three)
			next_entries.append(data[window_size][2]);

	#clf = linear_model.Ridge(alpha=0.1)
	#clf = linear_model.BayesianRidge()
	#clf = SVR(kernel='linear', C=1e3)
	#clf = LogisticRegression(C=1, penalty='l2', tol=0.01)
	#clf = linear_model.LinearRegression()
	#clf = linear_model.Perceptron()
	clf = Pipeline([('poly', PolynomialFeatures(degree=3)), ('linear', linear_model.LinearRegression(fit_intercept=False))])
	clf.fit(input_features, next_entries)
	total_error = 0
	num = 0

	for elem, data in held_out.iteritems():
		if len(data) > window_size:
			input_features = [data[i][2] for i in range(window_size)]
			# input_features = [data[0][2]]
			# for i in range(1, window_size):
			# 	input_features.append(data[i][2] - data[i - 1][2])
			input_features.append(data[0][0] - 1958)
			input_features.append(data[0][1])
			
			prediction = clf.predict(input_features)[0]
			actual = data[window_size][2]
			print 'Predicted: %d' % prediction
			print 'Actual: %d' % actual
			print

			difference = abs(prediction - actual)
			total_error += difference
			num += 1

	print 'Average error for fold %d: %f' % (fold_num, float(total_error) / num)
	return float(total_error) / num





if __name__ == '__main__':
	main()
