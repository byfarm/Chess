import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

print(tf.config.list_physical_devices('GPU'))


def to_bits(board: object) -> np.ndarray:
	"""
	creates a bitboard of all moves
	:param board: the gamestate
	:return bit_board: a 3d np array of bit boards
	"""
	# ======================= pieces ==========================
	# create a bit dictionay that will house each bitboard corresponding to the piece
	bit_dictionary = {}

	for piece_color in board.pieces.keys():
		for piece_type in board.pieces[piece_color].keys():
			bit_dictionary[piece_color + piece_type] = np.zeros((8, 8), int)
			for piece in board.pieces[piece_color][piece_type]:
				bit_dictionary[piece.name][piece.position] = 1

	# ====================== all moves and captures =========================
	opponent_moves_and_captures = board.find_machine_moves(color=board.oppo_turn)
	opponent_moves = opponent_moves_and_captures[0]
	opponent_captures = opponent_moves_and_captures[-1]

	bit_dictionary["w_moves"] = np.zeros((8, 8), int)
	bit_dictionary["b_moves"] = np.zeros((8, 8), int)
	# this adds values to the bitboards for the current move
	key_turn = board.move_turn + "_moves"
	for possible_moves in board.legal_moves:
		attacked_space = possible_moves[0][1]
		bit_dictionary[key_turn][attacked_space] = 1

	# this adds values to the bitboards for the current move
	key_turn = board.oppo_turn + "_moves"
	for possible_moves in opponent_moves:
		attacked_space = possible_moves[0][1]
		bit_dictionary[key_turn][attacked_space] = 1

	bit_dictionary["b_capture"] = np.zeros((8, 8), int)
	bit_dictionary["w_capture"] = np.zeros((8, 8), int)
	# adds values to the bitboards for opponent's captures
	key_turn = board.oppo_turn + "_capture"
	for possible_moves in opponent_captures:
		attacked_space = possible_moves[1]
		bit_dictionary[key_turn][attacked_space] = 1

	# adds values to the bitboards for opponent's captures
	key_turn = board.move_turn + "_capture"
	for possible_moves in board.capturing_location:
		attacked_space = possible_moves[1]
		bit_dictionary[key_turn][attacked_space] = 1

	# ================ castling =======================
	# layer for all legal castles
	castling_bitboard = np.zeros((8, 8), int)
	for white_rook in board.pieces['w']['R']:
		if not white_rook.moved and not board.pieces["w"]["K"][0].moved:
			castling_bitboard[0, white_rook.position] = 1

	for black_rook in board.pieces['b']['R']:
		if not black_rook.moved and not board.pieces["b"]["K"][0].moved:
			castling_bitboard[0, black_rook.position] = 1
	bit_dictionary["castling"] = castling_bitboard

	# ================== move turn =========================
	# layer for the color
	if board.move_turn == "w":
		move_turn_bitboard = np.zeros((8, 8), dtype=int)
	else:
		move_turn_bitboard = np.ones((8, 8), dtype=int)
	bit_dictionary["move_turn"] = move_turn_bitboard

	bitboard_list = [bit_dictionary[key] for key in bit_dictionary.keys()]

	# =================== combination ========================
	# makes it into a tensorflow array
	bitboard = np.stack(bitboard_list)
	bitboard = tf.convert_to_tensor(bitboard, dtype=tf.int8)
	"""# expands upon the bitboard so that every possible move has the move from and the move to
	for i in range(14, 14 + 218):
		try:
			move = board.legal_moves[i][0]
			bitboard[i, move[0][0], move[0][1]] = 1
			bitboard[i, move[1][0], move[1][1]] = 1
		except IndexError:
			break"""

	return tf.expand_dims(bitboard, axis=0)

def to_bits(board):
	"""
	creates a bitboard of all moves
	:param board: the gamestate
	:return bit_board: a 3d np array of bit boards
	"""
	# ======================= pieces ==========================
	# create a bit dictionay that will house each bitboard corresponding to the piece
	bit_dictionary = {}

	for piece_color in board.pieces.keys():
		for piece_type in board.pieces[piece_color].keys():
			bit_dictionary[piece_color + piece_type] = tf.Variable(tf.zeros((8, 8), tf.int8))
			for piece in board.pieces[piece_color][piece_type]:
				bit_dictionary[piece.name][piece.position].assign(1)

	# ====================== all moves and captures =========================
	opponent_moves_and_captures = board.find_machine_moves(color=board.oppo_turn)
	opponent_moves = opponent_moves_and_captures[0]
	opponent_captures = opponent_moves_and_captures[-1]

	bit_dictionary["w_moves"] = tf.Variable(tf.zeros((8, 8), tf.int8))
	bit_dictionary["b_moves"] = tf.Variable(tf.zeros((8, 8), tf.int8))
	# this adds values to the bitboards for the current move
	key_turn = board.move_turn + "_moves"
	for possible_moves in board.legal_moves:
		attacked_space = possible_moves[0][1]
		bit_dictionary[key_turn][attacked_space].assign(1)

	# this adds values to the bitboards for the current move
	key_turn = board.oppo_turn + "_moves"
	for possible_moves in opponent_moves:
		attacked_space = possible_moves[0][1]
		bit_dictionary[key_turn][attacked_space].assign(1)

	bit_dictionary["b_capture"] = tf.Variable(tf.zeros((8, 8), tf.int8))
	bit_dictionary["w_capture"] = tf.Variable(tf.zeros((8, 8), tf.int8))
	# adds values to the bitboards for opponent's captures
	key_turn = board.oppo_turn + "_capture"
	for possible_moves in opponent_captures:
		attacked_space = possible_moves[1]
		bit_dictionary[key_turn][attacked_space].assign(1)

	# adds values to the bitboards for opponent's captures
	key_turn = board.move_turn + "_capture"
	for possible_moves in board.capturing_location:
		attacked_space = possible_moves[1]
		bit_dictionary[key_turn][attacked_space].assign(1)

	# ================ castling =======================
	# layer for all legal castles
	castling_bitboard = tf.Variable(tf.zeros((8, 8), tf.int8))
	for white_rook in board.pieces['w']['R']:
		if not white_rook.moved and not board.pieces["w"]["K"][0].moved:
			castling_bitboard[white_rook.position].assign(1)

	for black_rook in board.pieces['b']['R']:
		if not black_rook.moved and not board.pieces["b"]["K"][0].moved:
			castling_bitboard[black_rook.position].assign(1)
	bit_dictionary["castling"] = castling_bitboard

	# ================== move turn =========================
	# layer for the color
	if board.move_turn == "w":
		move_turn_bitboard = tf.zeros((8, 8), dtype=tf.int8)
	else:
		move_turn_bitboard = tf.ones((8, 8), dtype=tf.int8)
	bit_dictionary["move_turn"] = move_turn_bitboard

	bitboard_list = [bit_dictionary[key] for key in bit_dictionary.keys()]

	# =================== combination ========================
	# makes it into a tensorflow array
	bitboard = tf.stack(bitboard_list)
	"""# expands upon the bitboard so that every possible move has the move from and the move to
	for i in range(14, 14 + 218):
		try:
			move = board.legal_moves[i][0]
			bitboard[i, move[0][0], move[0][1]] = 1
			bitboard[i, move[1][0], move[1][1]] = 1
		except IndexError:
			break"""

	return tf.expand_dims(bitboard, axis=0)


def policy_NN():
	tf.config.list_physical_devices('GPU')
	# inits the policy Neural Network
	policy = keras.models.Sequential(name="policy")
	policy.add(layers.Conv2D(18, (2, 2), padding='valid', activation='relu', input_shape=(18, 8, 8)))
	policy.add(layers.MaxPool2D((2, 2)))
	policy.add(layers.Conv2D(28, (2, 2), activation='relu'))
	policy.add(layers.MaxPool2D((2, 2)))
	policy.add(layers.Flatten())
	policy.add(layers.Dense(536, activation='relu'))
	policy.add(layers.Dense(218, activation='softmax'))
	loss = keras.losses.CategoricalCrossentropy()
	optim = keras.optimizers.Adam(learning_rate=0.2)
	metrics = ["accuracy"]
	policy.compile(optimizer=optim, loss=loss, metrics=metrics)
	policy.summary()
	return policy


def value_NN():
	# inits the value Neural Network
	value = keras.models.Sequential(name="value")
	value.add(layers.Conv2D(18, (2, 2), padding='valid', activation='relu', input_shape=(18, 8, 8)))
	value.add(layers.MaxPool2D((2, 2)))
	value.add(layers.Conv2D(32, (2, 2), activation='relu'))
	value.add(layers.MaxPool2D((2, 2)))
	value.add(layers.Flatten())
	value.add(layers.Dense(56, activation='relu'))
	value.add(layers.Dense(1, activation='relu'))
	loss = keras.losses.MeanSquaredError()
	optim = keras.optimizers.Adam(learning_rate=0.2)
	metrics = ["accuracy"]
	value.compile(optimizer=optim, loss=loss, metrics=metrics)
	value.summary()
	return value




