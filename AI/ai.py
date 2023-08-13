import tensorflow as tf


def to_bits(board: object) -> tf.Tensor:
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
			bit_dictionary[piece_color + piece_type] = tf.Variable(tf.zeros((8, 8), tf.uint8))
			for piece in board.pieces[piece_color][piece_type]:
				bit_dictionary[piece.name][piece.position].assign(1)

	# ====================== all moves and captures =========================
	opponent_moves_and_captures = board.find_machine_moves(color=board.oppo_turn)
	opponent_moves = opponent_moves_and_captures[0]
	opponent_captures = opponent_moves_and_captures[-1]

	bit_dictionary["w_moves"] = tf.Variable(tf.zeros((8, 8), tf.uint8))
	bit_dictionary["b_moves"] = tf.Variable(tf.zeros((8, 8), tf.uint8))
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

	bit_dictionary["b_capture"] = tf.Variable(tf.zeros((8, 8), tf.uint8))
	bit_dictionary["w_capture"] = tf.Variable(tf.zeros((8, 8), tf.uint8))
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
	castling_bitboard = tf.Variable(tf.zeros((8, 8), tf.uint8))
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
		move_turn_bitboard = tf.zeros((8, 8), dtype=tf.uint8)
	else:
		move_turn_bitboard = tf.ones((8, 8), dtype=tf.uint8)
	bit_dictionary["move_turn"] = move_turn_bitboard

	# =================== combination ========================
	bitboard_list = [bit_dictionary[key] for key in bit_dictionary.keys()]
	# makes it into a tensorflow array
	bitboard = tf.stack(bitboard_list)

	return tf.expand_dims(bitboard, axis=0)







