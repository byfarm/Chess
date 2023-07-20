import numpy as np
import chess


def to_bits(board: object):
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

	# creates the bitboard and makes it into a 3d numpy array
	bitboard = np.empty((14, 8, 8), int)
	dictionary_keys = list(bit_dictionary.keys())
	for i in range(len(dictionary_keys)):
		key = dictionary_keys[i]
		bitboard[i, :, :] = bit_dictionary[key]

	return bitboard


def position_evaluation(board: np.ndarray):
	"""
	evaluates the current board position
	:return:
	"""
	pass
