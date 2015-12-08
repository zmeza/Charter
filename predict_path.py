#!/usr/bin/python -tt

import pygn
import sys
from sklearn import linear_model
import scipy
import json

DELIM = ':::'

def main():
	args = sys.argv[1:]
	window_size = int(args[0])

	ftrain = open('data/train_paths.json', 'r')
	train_data_json = json.load(ftrain) # is a map

	ftest = open('data/test_paths.json', 'r')
	test_data_json = json.load(ftest)

	song_to_gold_map = {}
	song_to_predict_map = {}

	song_to_error_map = {}

	model = train(train_data_json, window_size)

	predict_paths(test_data_json, song_to_gold_map, song_to_predict_map, model, window_size)

	for elem in song_to_gold_map:
		gold = song_to_gold_map[elem]
		predict = song_to_predict_map[elem]

		if len(gold) < window_size * 2: continue
		total_error = 0
		for i in range(window_size - 1, len(gold)):
			total_error += abs(gold[i] - predict[i])

		print total_error, float(len(gold)), 1.0 * total_error / float(len(gold))
		song_to_error_map[elem] = 1.0 * total_error / float(len(gold))

	print song_to_error_map


	total_2015_error = 0
	num_2015 = 0

	sorted_keys = sorted(song_to_error_map, key=lambda x : song_to_error_map[x])
	for key in sorted_keys:
		# print '%s: %f' % (key, song_to_error_map[key])
		year = 2015
		
		if test_data_json[key][0][0] == year:
			num_2015 += 1
			total_2015_error += song_to_error_map[key]
			print '%s: %f' % (key, song_to_error_map[key])
			print len(song_to_gold_map[key])
			print 'gold: ' + str(song_to_gold_map[key])
			print 'predict: ' + str(song_to_predict_map[key])
			print

	print '2015 error: %f (%d songs)' % (1.0 * total_2015_error / num_2015, num_2015)

	# for i in range(10):

	# 	print '%s: %f' % (sorted_keys[i], song_to_error_map[sorted_keys[i]])
	# 	print 'gold: ' + str(song_to_gold_map[sorted_keys[i]])
	# 	print 'predict: ' + str(song_to_predict_map[sorted_keys[i]])
	# 	print


def train(data_dict, window_size):
	input_features = []
	next_entries = []
	for elem, data in data_dict.iteritems():
		song, artist = elem.split(DELIM)
		if len(data) > window_size:
			for k in range(0, len(data) - window_size):
				first_three = [data[k + i][2] for i in range(window_size)]
				# first_three = [data[k][2]]
				# for i in range(1, window_size):
				# 	first_three.append(data[k + i][2] - data[k + i - 1][2])

				first_three.append(data[0][0] - 1958)
				first_three.append(data[0][1])

				input_features.append(first_three)
				next_entries.append(data[k + window_size][2]);

	clf = linear_model.Ridge(alpha=0.1)
	clf.fit(input_features, next_entries)

	return clf


def predict_paths(data_dict, song_to_gold_map, song_to_predict_map, model, window_size):
	for elem, data in data_dict.iteritems():
		if len(data) > window_size:
			predict_path = [data[i][2] for i in range(window_size)]

			gold_len = len(data)

			input_features = [data[i][2] for i in range(window_size)]
			# input_features = [data[0][2]]
			# for i in range(1, window_size):
			# 	input_features.append(data[i][2] - data[i - 1][2])

			input_features.append(data[0][0] - 1958)
			input_features.append(data[0][1])

			prediction = model.predict(input_features)[0]
			predict_path.append(prediction)


			for k in range(window_size, gold_len - 1):
				input_features = input_features[1:3]
				input_features.append(prediction)
				input_features.append(data[0][0] - 1958)
				input_features.append(data[0][1])

				prediction = model.predict(input_features)[0]
				predict_path.append(prediction)


			gold_path = [data[i][2] for i in range(len(data))]

			song_to_gold_map[elem] = gold_path
			song_to_predict_map[elem] = predict_path
			# print predict_path, gold_path
			# print len(predict_path), len(gold_path)
			# print

			# input_features = [data[i][2] for i in range(window_size)]
			# # input_features = [data[0][2]]
			# # for i in range(1, window_size):
			# # 	input_features.append(data[i][2] - data[i - 1][2])
			# input_features.append(data[0][0] - 1958)
			# input_features.append(data[0][1])
			
			# prediction = clf.predict(input_features)[0]
			# actual = data[window_size][2]
			# print 'Predicted: %d' % prediction
			# print 'Actual: %d' % actual
			# print

			# difference = abs(prediction - actual)
			# total_error += difference
			# num += 1


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

	clf = linear_model.Ridge(alpha=0.1)
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
