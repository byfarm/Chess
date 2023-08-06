import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def to_bits(board: object) -> np.ndarray:
	"""
	creates a bitboard of all moves
	:param board: the gamestate
	:return bit_board: a 3d np array of bit boards
	"""
	# create a bit dictionay that will house each bitboard corresponding to the piece
	bit_dictionary = {}
	for rank in board.board:
		for space in rank:
			if space != "EE":
				bit_dictionary[space] = np.zeros((8, 8), int)
	# these two bitboards are for possible moves for the machine
	bit_dictionary["wc"] = np.zeros((8, 8), int)
	bit_dictionary["bc"] = np.zeros((8, 8), int)

	# adds all positions of the pieces into the bitboard
	for black_and_white_pieces in board.pieces.values():
		for piece_type in black_and_white_pieces.values():
			for piece in piece_type:
				bit_dictionary[piece.name][piece.position] = 1

	# this adds values to the bitboards for the current move
	key_turn = board.move_turn + "c"
	for possible_moves in board.legal_moves:
		attacked_space = possible_moves[0][1]
		bit_dictionary[key_turn][attacked_space] = 1

	# adds values to the bitboards for opponent's move
	opponent_moves = board.find_machine_moves()[0]
	key_turn = board.oppo_turn + "c"
	for possible_moves in opponent_moves:
		attacked_space = possible_moves[0][1]
		bit_dictionary[key_turn][attacked_space] = 1

	# creates the bitboard and makes it into a 3d numpy array for all the positions and possible moves at once
	# can reset to depth of 232
	bitboard = np.zeros((1, 14, 8, 8), int)
	dictionary_keys = list(bit_dictionary.keys())
	for i in range(len(dictionary_keys)):
		key = dictionary_keys[i]
		bitboard[0, i, :, :] = bit_dictionary[key]

	"""# expands upon the bitboard so that every possible move has the move from and the move to
	for i in range(14, 14 + 218):
		try:
			move = board.legal_moves[i][0]
			bitboard[i, move[0][0], move[0][1]] = 1
			bitboard[i, move[1][0], move[1][1]] = 1
		except IndexError:
			break"""

	return bitboard


def policy_NN():
	# inits the policy Neural Network
	policy = keras.models.Sequential()
	policy.add(layers.Conv2D(14, (2, 2), padding='valid', activation='relu', input_shape=(14, 8, 8)))
	policy.add(layers.MaxPool2D((2, 2)))
	policy.add(layers.Conv2D(14, (2, 2), padding='valid', activation='relu', input_shape=(14, 8, 8)))
	policy.add(layers.Flatten())
	policy.add(layers.Dense(564, activation='relu'))
	policy.add(layers.Dense(218, activation='softmax'))
	loss = keras.losses.CategoricalCrossentropy()
	optim = keras.optimizers.Adam(learning_rate=0.1)
	policy.compile(optimizer=optim, loss=loss)
	policy.summary()
	return policy


def value_NN():
	# inits the value Neural Network
	value = keras.models.Sequential()
	value.add(layers.Conv2D(14, (2, 2), padding='valid', activation='relu', input_shape=(14, 8, 8)))
	value.add(layers.MaxPool2D((2, 2)))
	value.add(layers.Flatten())
	value.add(layers.Dense(1, activation='relu'))
	loss = keras.losses.MeanSquaredError()
	optim = keras.optimizers.Adam(learning_rate=0.1)
	value.compile(optimizer=optim, loss=loss)
	value.summary()
	return value

