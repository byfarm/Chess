import copy
import numpy as np
from rules_and_func.pieces import *


class MachineBoard:
	"""
	Is the overall driver for the game. has the board and all the rules
	"""
	def __init__(self):

		self.board = np.array([
			['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
			['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
			['EE', 'EE', 'EE', 'EE', 'EE', 'EE', 'EE', 'EE'],
			['EE', 'EE', 'EE', 'EE', 'EE', 'EE', 'EE', 'EE'],
			['EE', 'EE', 'EE', 'EE', 'EE', 'EE', 'EE', 'EE'],
			['EE', 'EE', 'EE', 'EE', 'EE', 'EE', 'EE', 'EE'],
			['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
			['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']])
		self.move_log = []
		self.move_turn = 'w'
		self.oppo_turn = 'b'
		self.move_counter = 1
		self.pieces = {
			'w': {'R': [], 'P': [], 'B': [], 'N': [], 'Q': [], 'K': []},
			'b': {'R': [], 'P': [], 'B': [], 'N': [], 'Q': [], 'K': []}
		}
		self.stalemate = False
		# moves will be the possible spaces that can move to ex: (3, 2)
		self.show_board = None
		self.white_win = None
		# initialize draw lists
		self.past_moves_pieces = []
		self.past_boards = []

		# initialize tree values
		self.name = "Head"
		self.value = None
		self.initialize_pieces()

		self.check_board = Check_Board(pieces=self.pieces, board=self.board, move_turn=self.move_turn, oppo_turn=self.oppo_turn)

		# find moves in position
		self.legal_moves, self.castling_moves, self.captures, self.capturing_location = self.find_machine_moves()

	def __repr__(self):
		return f'Chess Game'

	def move(self, old_position: tuple, input_move: tuple):
		"""
		moves a piece on the board by updating board
		:param input_move: tuple
			position of piece currently
		:param old_position: tuple
			where want piece to move
		:notes
			move will be valid beforehand
		"""
		# use the piece that is being used
		piece = self.board[old_position]
		enemy_piece = self.board[input_move]

		# changes space piece moved from to empty, changes the new space to the piece
		self.board[old_position] = 'EE'
		self.board[input_move] = piece
		# if capturing another piece, use the dictionary to find which piece and delete it
		if enemy_piece[0] != 'E':
			for pic in self.pieces[enemy_piece[0]][enemy_piece[1]]:
				if pic.position == input_move:
					self.pieces[enemy_piece[0]][enemy_piece[1]].remove(pic)
					del pic
					break

		# reset the pieces object's position
		for pic in self.pieces[piece[0]][piece[1]]:
			if pic.position == old_position:
				pic.position = input_move
				break


	def print_game(self):
		"""
		prints the current board in a more readable form. or it prints a str output. will have to call from outside the
		class
		"""
		printable = self.board
		new_print = np.core.defchararray.replace(printable, 'EE', '/ ')
		hor = np.array([' a', ' b', ' c', ' d', ' e', ' f', ' g', ' h'], dtype=str)
		v1 = np.empty((9, 1), dtype=str)
		for i in range(8, -1, -1):
			v1[8 - i] = f'{i} '
		pr = np.vstack((new_print, hor))
		show_board = np.hstack((v1, pr))
		print(f'\n{show_board}')

	def print_board(self, printable):
		# makes it so all board prints are supressed in the copy boards
		if type(printable) == np.ndarray:
			pass
		else:
			print(f'\n{printable}')

	def next_turn(self):
		"""
		moves the game onto the next turn
		"""
		if self.move_turn == 'w':
			self.move_turn = 'b'
			self.oppo_turn = 'w'
		elif self.move_turn == 'b':
			self.move_counter += 1
			self.move_turn = 'w'
			self.oppo_turn = 'b'

	def initialize_single_piece(self, name: str, position: tuple):
		"""
		initializes a single piece into the game. updates the games piece list
		:param name: str
			name of piece being initialized
		:param position: tuple
			(row, column) of where piece is being initialized
		"""
		# checks which piece each is and initializes the object, appending it into the board's list of pieces
		# piece is the piece type
		piece = name[-1]
		color = name[0]
		piece_o = None
		if piece == 'P':
			piece_o = Pawn(name, position)
		elif piece == 'K':
			piece_o = King(name, position)
		elif piece == 'Q':
			piece_o = Queen(name, position)
		elif piece == 'R':
			piece_o = Rook(name, position)
		elif piece == 'N':
			piece_o = Knight(name, position)
		elif piece == 'B':
			piece_o = Bishop(name, position)
		if color != 'E':
			# seperate in colors and add into dict
			self.pieces[color][piece].append(piece_o)

	def initialize_pieces(self):
		"""
		makes the pieces all objects and appends them into the board
		"""
		# uses counters to tell where each piece is located
		row_c = 0
		while row_c < 8:
			column_c = 0
			while column_c < 8:
				# name is the letters represented on the board
				name = self.board[row_c, column_c]
				# position is where the counter is and where the piece is
				position = (row_c, column_c)
				# initialize each piece induvidualy
				self.initialize_single_piece(name, position)
				column_c += 1
			row_c += 1
		# print the starting position of the board
		#self.print_board(self.board)

	def find_machine_moves(self, color=None):
		"""
		finds all possible moves for the machine
		:return legal_moves: list of tuple
			[((4,5), (3,4), e_passant, [bool, rook, checked_spaces]), ... ]
		"""
		legal_moves = []
		castling_moves = []
		capturing_squares = []
		capturing_location = []
		# find pieces in same color
		if color is None:
			color = self.move_turn

		piece_dictionary = self.pieces[color]

		for p in piece_dictionary.values():
			for piece in p:
				# for every place on the board, see if each piece can capture/move to that place
				for n in range(0, 8):
					for idx in range(0, 8):
						# if pawn, different move from capture so only want to look at capture
						end = (n, idx)
						start = piece.position
						if end != start:
							move = [start, end]
							if self.board[start][1] == 'E':
								print(piece, move)
							leg_move, e_passant, castle, capture = self.check_if_machine_move_is_legal(move)
							if leg_move is True:
								tot_mv = (move, e_passant, castle)
								# each entry will be: ([(5,4),(4,3)], e_pasant, [castleability, rook, spaces])
								legal_moves.append(tot_mv)
								if castle is not None:
									pass
								if castle is None or not castle[0]:
									castling_moves.append(tot_mv[0])
								if capture is not None:
									capturing_squares.append(capture)
									capturing_location.append(tot_mv[0])


		# outputs legal moves, castling_moves: check moves, and capturing squares
		return legal_moves, castling_moves, capturing_squares, capturing_location

	def play_machine_move(self, move: list[tuple, bool, list[bool, object, list[tuple]]], check_board=False):
		"""
		actually makes the move
		:param move: tuple
			([(5,4),(4,3)], e_pasant, [castleability, rook, spaces])
		:return: makes the move and moves onto the next turn
		"""
		# append the current board into the past boards for draw
		curr_board = self.board.copy()
		self.past_boards.append(curr_board)

		# break apart move
		move_spaces = move[0]
		e_passant = move[1]
		castle = move[2]

		# splice the move
		color, piece, original_position, new_position = self.splice_machine_move(move_spaces)

		# add captured piece for draw
		captured = self.board[move_spaces[1]][1]

		# check if ep or castle true
		if e_passant is True:
			self.move_ep_machine(original_position, new_position)
			captured = 'P'
		elif castle is not None and castle[0] is True:
			# find the correct king
			king = self.pieces[self.move_turn]['K'][0]
			rook, spaces = self.find_machine_castle_pieces(new_position, king)
			self.move_castle(king, rook, spaces)
		else:
			self.move(original_position, new_position)

		# check if a pawn has been promoted
		self.promotion_check()

		self.change_move_value(piece, new_position)

		# add move to past move for draw condition
		if piece == 'P' or captured != 'E':
			self.past_moves_pieces.append(True)
		else:
			self.past_moves_pieces.append(False)

		# go onto next turn and print the board and add move to log
		self.move_log.append(move)
		# reset all the possible moves
		self.next_turn()

		# move the check board forward:
		if check_board:
			self.check_board.play_machine_move(move, check_board=False)

		# find moves in position
		self.legal_moves, self.castling_moves, self.captures, self.capturing_location = self.find_machine_moves()
		#self.print_board(self.board)

	def change_move_value(self, piece: str, new_position: tuple):
		"""
		checks if r, k, or p has moved and if it has will update its moved value to true
		:param piece: the piece being moved
		:param new_position: the position it is moving to
		:return: updates the piece's moved value
		"""
		if piece == 'R' or piece == 'K' or piece == 'P':
			piece_type = self.pieces[self.move_turn][piece]
			for i in piece_type:
				if i.position == new_position:
					i.moved = True

	def promotion_check(self):
		'''
		checks to see if a pawn has been promoted. if it has, it promotes it
		'''
		# check for promotion
		for i in (self.pieces['w']['P'] + self.pieces['b']['P']):
			if i.position[0] == 0 or i.position[0] == 7:
				promotion_piece = 'Q'
				nm = i.promotion(self, promotion_piece)
				self.board[i.position] = nm

	def splice_machine_move(self, move: list):
		"""
		splices the move so you know your outputs
		:param move: list of tuple
		:return color: str
			color of piece
		:return piece: str
			piece type 'R'
		:return original_position: tuple
			where move coming from
		:return new_position: tuple
			where move going to
		"""
		original_position, new_position = move[0], move[1]
		piece = self.board[original_position]
		color = piece[0]
		piece = piece[1]
		return color, piece, original_position, new_position

	def check_if_machine_move_is_legal(self, move: list):
		"""
		is the overall process for making a move.
		:param move: list of tuple
			[(4,3), (6,4)]
		:return move played: bool
			if the move has been played or not
		:return e_passant: bool
			if the move is ean passant or not
		:return piece: str
			the piece that is being moved
		:return castle: bool
			whether move is castle or not
		"""
		move_played = False
		# splice the input
		color, piece, original_position, new_position = self.splice_machine_move(move)

		# see if the piece can move there
		legal_move, capture, e_passant, castle = self.find_if_machine_piece_can_move(color, piece, original_position, new_position)
		# if legal move is true, make sure it is not a move that puts the king in check
		if legal_move is False or legal_move is None:
			move_played = False

		elif legal_move is True:
			in_check = self.check_board.check_if_move_makes_check((move, e_passant, castle))
			# in_check = self.machine_move_in_check(original_position, new_position, e_passant)
			# check for the in check is T or false
			if in_check is False:
				# set move to true
				move_played = True
			else:
				move_played = False
		return move_played, e_passant, castle, capture

	def machine_move_in_check(self, org_pos: tuple, new_pos: tuple, e_passant: bool):
		"""
		checks to see if making the move will put you in check
		:param org_pos: space move coming from
		:param new_pos: space move going to
		:param e_passant: whether e_passant is true
		:return in_check: bool
			whether the move will put you in check or not
		"""
		# TODO: instead of copy temporarily move the piece then reset, need to make a new move funciton "temp move"
		# complicated for castles and en pessant
		copy_board = copy.deepcopy(self)

		if e_passant is True:
			copy_board.move_ep_machine(org_pos, new_pos)

		else:
			copy_board.move(org_pos, new_pos)

		in_check = self.check_for_checks(copy_board)

		# if there is a legal move that attacks the king then he is in check
		return in_check

	def check_for_checks(self, game: object, s_turn=None, o_turn=None):
		in_check = False
		if s_turn is None:
			s_turn = self.move_turn
		if o_turn is None:
			o_turn = self.oppo_turn
		# look for the possible moves of the other side, then see if any of them put the king in check
		for k in game.pieces[o_turn].values():
			for p in k:
				try:
					in_check = game.find_if_machine_piece_can_move(
						p.color, p.name[1], p.position, game.pieces[s_turn]['K'][0].position)[0]
				except IndexError:
					in_check = True
				if in_check:
					return in_check
		if not in_check:
			in_check = False
			return in_check

	def find_if_machine_piece_can_move(self, color: str, piece: str, original_position: tuple, new_position: tuple):
		"""
		goes through the piece it is (including castling and ep) and sees if the move is allowed
		:param color: which color the piece is
		:param piece: which piece type it is
		:param original_position: where moving from
		:param new_position: where moving to
		:return legal move: bool
			whether move is legal or not
		:return capture: str
			space the move is to
		:return e_passant: bool
			whether the move was ep or not
		:return castle: list
			bool of whether castled, the rook object, the important castling spaces
		"""
		# find out which piece type it is
		all_pieces = self.pieces[color]
		if piece == 'E':
			print(original_position, new_position)
		piece = piece[-1:]
		piece_type = all_pieces[piece]
		# initialize vairables
		legal_move, capture, e_passant, castle = None, None, None, None

		# if it is a pawn, check if it is trying to capture. if is, check if move is legal and what is captured
		if piece == 'P':
			if original_position[1] != new_position[1]:
				for pawn in piece_type:
					if pawn.position == original_position:
						legal_move, capture, e_passant = pawn.capture(new_position, self.board, self.move_log)
			# if not capturing, check if move is legal
			else:
				for pawn in piece_type:
					if pawn.position == original_position:
						legal_move = pawn.check_legal_move(new_position, self.board)

		# if piece is king, see if king has moved
		elif piece == 'K':
			for king in piece_type:
				# if diff rows == 2, back rank, correct king, and king hasn't moved
				if abs(new_position[1] - original_position[1]) == 2 and \
						((new_position[0] == 0 and self.move_turn == 'b') or
						 (new_position[0] == 7 and self.move_turn == 'w')) and \
						king.moved is False and\
						new_position[0] == original_position[0]:
					legal_move, castle = self.machine_legal_castle(new_position, king)
					if castle is False:
						legal_move = False
				else:
					legal_move, capture = king.check_legal_move(new_position, self.board)

		# if the piece is not a pawn or k, identify which piece is trying to move and check if the move is legal
		else:
			for pawn in piece_type:
				if pawn.position == original_position:
					(legal_move, capture) = pawn.check_legal_move(new_position, self.board)

		return legal_move, capture, e_passant, castle

	def find_machine_castle_pieces(self, new_pos: tuple, king: object):
		"""
		find the rook and the spaces needed to castle
		:param king: the king object you are trying to move
		:param new_pos: the move inputed
		:return important_rook: object
			the rook to be castled with
		:return empty_spaces: list of tuple
			the spaces important for castling
		"""
		rooks = self.pieces['w']['R'] + self.pieces['b']['R']
		important_rook, empty_spaces = None, None
		if new_pos in [(7, 4), (7, 5), (7, 6)] and king.color == 'w':
			empty_spaces = [(7, 4), (7, 5), (7, 6)]
			# find the correct rook
			for i in rooks:
				if i.color == self.move_turn and i.position == (7, 7):
					important_rook = i
		elif new_pos in [(0, 4), (0, 5), (0, 6)] and king.color == 'b':
			empty_spaces = [(0, 4), (0, 5), (0, 6)]
			for i in rooks:
				if i.color == self.move_turn and i.position == (0, 7):
					important_rook = i

		# this is for castle long
		elif new_pos in [(7, 4), (7, 3), (7, 2), (7, 1)] and king.color == 'w':
			empty_spaces = [(7, 4), (7, 3), (7, 2), (7, 1)]
			for i in rooks:
				if i.color == self.move_turn and i.position == (7, 0):
					important_rook = i
		elif new_pos in [(0, 4), (0, 3), (0, 2), (0, 1)] and king.color == 'b':
			empty_spaces = [(0, 4), (0, 3), (0, 2), (0, 1)]
			for i in rooks:
				if i.color == self.move_turn and i.position == (0, 0):
					important_rook = i
		return important_rook, empty_spaces

	def machine_legal_castle(self, new_pos: tuple, king: object):
		"""
		find if the imputed move allows for castling
		:param king: the king object you are trying to move
		:param new_pos: imputed move
		:return legal_move: whether the move is legal or not
		:return piece_castleability: whether the move is a castle
		:return rook: importnat rook object
		:return checked_spaces: list of the spaces for the movement funtion
		"""
		piece_castleability = True
		checked_spaces = None
		# find the rook and the spaces
		rook, spaces = self.find_machine_castle_pieces(new_pos, king)
		if rook is None or spaces is None or rook.moved is True:
			piece_castleability = False

		if spaces is not None:
			# do empy spaces check
			for i in spaces[1:]:
				if self.board[i] != 'EE':
					# if there is not all empty spaces, change castle to false
					piece_castleability = False
					legal_move = False
					break


			# reset empty spaces
			checked_spaces = spaces[:3]

			# check to see all moves to update the possilbe moves
			pieces = self.pieces[self.oppo_turn]

			for move in checked_spaces:
				for k in pieces.keys():
					for p in pieces[k]:
						if k != 'K':
							try:
								attacked = self.find_if_machine_piece_can_move(self.oppo_turn, p.name[1], p.position, move)[0]
							except IndexError:
								attacked = False
							if attacked:
								break

			# if space can be attacked, change castle to false
			if attacked:
				piece_castleability = False
				legal_move = False
			elif attacked is False:
				legal_move = True

			if len(spaces) == 4:
				checked_spaces = spaces[1:3]

		if piece_castleability is False:
			legal_move = False

		return legal_move, [piece_castleability, rook, checked_spaces]

	def move_ep_machine(self, old: tuple, new: tuple):
		"""
		will make the move if en pessant is the move
		:param old: tuple
			(row, column) of the position of the piece in the current state
		:param new: tuple
			position of where you want to move the piece
		:notes:
			if a piece is captured, it will go and delete it from the list of pieces
		"""
		# use the piece that is being used
		piece = self.board[old]
		last_move = self.move_log[-1]
		kind_of_new = last_move[0][1]

		enemy_piece = self.board[kind_of_new]

		# reset the pieces object's position
		piece_dictionary = self.pieces[self.move_turn]
		for i in piece_dictionary[piece[1]]:
			if i.position == old:
				i.position = new

		# changes space piece moved from to empty, changes the new space to the piece
		self.board[old] = 'EE'
		self.board[kind_of_new] = 'EE'
		self.board[new] = piece

		# if capturing another piece, use the dictionary to find which piece and delete it
		piece_dictionary = self.pieces[self.oppo_turn]
		lis = piece_dictionary[enemy_piece[-1]]
		for i in lis:
			if i.position == kind_of_new:
				lis.remove(i)

	def move_castle(self, king: object, rook: object, checked_spaces: list):
		"""
		does the movement on the board and changes the attributes of each of the piece's
		:param king: object
			king object that needs to move
		:param rook: object
			rook object that needs to move
		:param checked_spaces:
			the spaces the pieces are moving through
		:notes
			will check if valid castle move beforehand
		"""
		if len(checked_spaces) == 3:
			# intitalize new spaces
			new_k_pos = checked_spaces[-1]
			new_r_pos = checked_spaces[-2]
		else:
			new_k_pos = checked_spaces[-2]
			new_r_pos = checked_spaces[-3]
		# initialize old spaces
		old_k_pos = king.position
		old_r_pos = rook.position
		# move the objects
		king.position = new_k_pos
		rook.position = new_r_pos
		# change the old spaces to empty
		self.board[old_k_pos] = 'EE'
		self.board[old_r_pos] = 'EE'
		# change the new position to r/k
		self.board[new_k_pos] = f'{king.color}K'
		self.board[new_r_pos] = f'{rook.color}R'
		# update rook/king moved
		king.moved = True
		rook.moved = True

	def check_for_checkmate(self):
		"""
		check position to see if checkmate has occoured
		will update the checkmate condition
		note: only call at the start of a turn
		"""
		# go through all possible moves and see if the king is still in check after the move
		if len(self.legal_moves) == 0:
			self.stalemate = True
			in_check = self.check_for_checks(self)
			if in_check:
				if self.move_turn == 'w':
					self.white_win = False
			#		self.print_board('Black wins')
				else:
					self.white_win = True
			#		self.print_board('White wins')
			else:
			#	self.print_board('stalemate, game over')
				self.white_win = None

	def look_for_draws(self):
		w_pieces = []
		b_pieces = []
		piece_dictionary = {}
		for i in self.pieces['b'].keys():
			if i != 'K':
				piece_dictionary[i] = self.pieces['w'][i] + self.pieces['b'][i]

		pieces_in_play = \
			piece_dictionary['Q'] + \
			piece_dictionary['B'] + \
			piece_dictionary['R'] + \
			piece_dictionary['N'] + \
			piece_dictionary['P']
		for i in pieces_in_play:
			if i.color == 'w':
				w_pieces.append(i)
			else:
				b_pieces.append(i)
		# if there is a major piece or a pawn on the board, pass
		if len(piece_dictionary['Q']) > 0 or len(piece_dictionary['R']) > 0 or len(piece_dictionary['P']) > 0:
			pass
		# if there are no pieces left in play
		elif len(pieces_in_play) == 0:
			self.stalemate = True
			return
		#	self.print_board("Insufficient Material")
		# if there are two pieces left and they are both nights or bishops and they are on opposing sides
		elif len(pieces_in_play) == 2 and (len(piece_dictionary['N']) == 2 or len(piece_dictionary['B']) == 2) and len(w_pieces) == 1:
			if len(piece_dictionary['B']) == 2:
				# check to see if bishops on same color
				color = []
				for n in piece_dictionary['B']:
					sum_coords = n.position[0] + n.position[1]
					# can use the sum of the coordinates to see what color on
					if sum_coords % 2 == 1:
						color.append('w')
					else:
						color.append('b')
				# if on same colors, checkmate is still possible
				if color[1] != color[0]:
					self.stalemate = True
			#		self.print_board("Insufficient Material")
			else:
				self.stalemate = True
			#	self.print_board("Insufficient Material")

		# if passes all prior conditions, check 50 move rule
		if self.stalemate is False and self.move_counter > 50:
			fif_move_rule = self.check_for_fifty_move_draw()
			if fif_move_rule is True:
				self.stalemate = True
			#	self.print_board("Insufficient Material")
		# if passes prior condition, check if 3 move repition is true
		if self.stalemate is False and self.move_counter > 3:
			three_rep = self.check_three_rep()
			if three_rep is True:
				self.stalemate = True
			#	self.print_board("Insufficient Material")

		if self.stalemate is True:
			self.white_win = None

	def check_for_fifty_move_draw(self):
		"""
		checks the last 50 moves to see if a pawn move has been played or a capture has happened
		:return fifty_move_rule: bool
			T if either condition is True, else false
		"""
		last_fif_pic = self.past_moves_pieces[-50:]
		if sum(last_fif_pic) == 0:
			fifty_move_rule = True
		#	self.print_board('50 move rule')
		else:
			fifty_move_rule = False
		return fifty_move_rule

	def check_three_rep(self):
		"""
		checks all past positons to current board and if 3 are true returns 3
		:return three_rep: bool
			whether 3 move repitions draw has been met
		"""
		# bools to empty list
		lis = []
		for p_board in self.past_boards:
			if (self.board == p_board).all():
				lis.append(True)
		# if three bools are added then condition has been met 3 times
		if len(lis) >= 3:
			three_rep = True
		#	self.print_board('3 move repetision')
		else:
			three_rep = False
		return three_rep

	def eff_end(self):
		"""
		checks to see if the game is effectively over
		:return white_eff_win: bool, see if white has effectively won or not
		"""
		white_eff_win = None
		# create overall piece dictionary
		piece_dictionary = {}
		for i in self.pieces['b'].keys():
			if i != 'K':
				piece_dictionary[i] = self.pieces['w'][i] + self.pieces['b'][i]
		pieces_in_play = \
			piece_dictionary['Q'] + \
			piece_dictionary['B'] + \
			piece_dictionary['R'] + \
			piece_dictionary['N'] + \
			piece_dictionary['P']

		# find the total # white pieces
		white_pieces = []
		for i in self.pieces['w'].keys():
			white_pieces += self.pieces['w'].get(i)
		tot_w_pic = len(white_pieces)

		# find total # black pieces
		black_pieces = []
		for i in self.pieces['b'].keys():
			black_pieces += self.pieces['b'].get(i)
		tot_b_pic = len(black_pieces)

		# if opposing side has no pieces and you have a queen, rook or pawn
		if tot_b_pic == 0 and (len(self.pieces['w']['Q']) >= 1 or len(self.pieces['w']['R']) >= 1 or len(self.pieces['w']['P']) > 1):
			white_eff_win = True
		elif tot_w_pic == 0 and (len(self.pieces['b']['Q']) == 1 or len(self.pieces['b']['R']) == 1 or len(self.pieces['b']['P']) > 1):
			white_eff_win = False

		# if one pawn is left
		elif tot_b_pic == 0 and len(self.pieces['w']['P']) == 1:
			pawn = None
			for p in self.pieces['w']['P']:
				if p.position[1] == 0 or p.position[1] == 7:
					pawn = p
			if pawn is None:
				white_eff_win = True

		elif tot_w_pic == 0 and len(self.pieces['b']['P']) == 1:
			pawn = None
			for p in self.pieces['b']['P']:
				if p.position[1] == 0 or p.position[1] == 7:
					pawn = p
			if pawn is None:
				white_eff_win = False

		# winning conditions if 1 piece left
		elif len(pieces_in_play) == 1:
			if len(self.pieces['w']['Q']) == 1 or len(self.pieces['w']['R']) == 1 or len(self.pieces['w']['P']) >= 1:
				white_eff_win = True
			elif len(self.pieces['b']['Q']) == 1 or len(self.pieces['b']['R']) == 1 or len(self.pieces['b']['P']) >= 1:
				white_eff_win = False

		# winning conditions if 2 piece left
		elif len(pieces_in_play) == 2:
			if len(self.pieces['w']['B']) == 2 or (len(self.pieces['w']['B']) == 1 and len(self.pieces['w']['N']) == 1):
				white_eff_win = True
			elif len(self.pieces['b']['B']) == 2 or (len(self.pieces['b']['B']) == 1 and len(self.pieces['b']['N']) == 1):
				white_eff_win = False

		# score eval, basically rage quits if behind by too many points
		else:

			# find the total score of each side
			b_score = sum([p.value for p in black_pieces])

			w_score = sum([p.value for p in white_pieces])

			# if the score difference is >= 10, it is an effective win
			if w_score - b_score >= 10:
				white_eff_win = True
			elif b_score - w_score >= 10:
				white_eff_win = False

		return white_eff_win

	def streamiled_checker_beta(self):
		pass


class Check_Board(MachineBoard):
	def __init__(self, board, pieces, move_turn, oppo_turn):
		self.pieces = pieces
		self.board = board
		self.temporary_capture_piece = None
		self.original_position = None
		self.new_position = None
		self.ep_opposing_pawn_position = None
		self.move_log = []
		self.move_turn = move_turn
		self.oppo_turn = oppo_turn

	def temp_move_forward(self, move: tuple[list[tuple], bool, bool]):
		if move[1]:
			return self.temp_move_en_pessant(move)
		else:
			# splice apart move
			move = move[0]
			self.original_position = move[0]
			self.new_position = move[1]
			self_piece = self.board[self.original_position]
			opposing_piece = self.board[self.new_position]

			# modify game board
			self.board[self.original_position] = "EE"
			self.board[self.new_position] = self_piece

			# delete the captured piece
			if opposing_piece[0] != "E":
				for captured_piece in self.pieces[opposing_piece[0]][opposing_piece[1]]:
					if captured_piece.position == self.new_position:
						self.temporary_capture_piece = captured_piece
						self.pieces[opposing_piece[0]][opposing_piece[1]].remove(captured_piece)
						break

			# change position of moved piece
			for piece in self.pieces[self_piece[0]][self_piece[1]]:
				if piece.position == self.original_position:
					piece.position = self.new_position
					return piece

	def temp_move_backward(self, moved_piece: object):
		moved_piece.position = self.original_position
		if self.temporary_capture_piece:
			self.pieces[self.temporary_capture_piece.name[0]][self.temporary_capture_piece.name[1]].append(self.temporary_capture_piece)
			self.board[self.new_position] = self.temporary_capture_piece.name
		else:
			self.board[self.new_position] = "EE"
		self.board[self.original_position] = moved_piece.name


	def temp_move_backward_en_pessant(self, moved_piece: object):
		moved_piece.position = self.original_position
		self.pieces[self.temporary_capture_piece.name[0]][self.temporary_capture_piece.name[1]].append(self.temporary_capture_piece)
		self.board[self.original_position] = moved_piece.name
		self.board[self.new_position] = "EE"
		self.board[self.ep_opposing_pawn_position] = self.temporary_capture_piece.name

	def check_if_move_makes_check(self, move: tuple[list[tuple], bool, bool]):
		moved_piece = self.temp_move_forward(move)

		in_check = self.check_for_checks(self)

		if move[1]:
			self.temp_move_backward_en_pessant(moved_piece)
		else:
			self.temp_move_backward(moved_piece)
		return in_check

	def temp_move_en_pessant(self, move: tuple[list[tuple], bool, bool]):
		# splice apart move
		move = move[0]
		self.original_position = move[0]
		self.new_position = move[1]
		self.ep_opposing_pawn_position = self.move_log[-1][0][1]
		self_piece = self.board[self.original_position]
		opposing_piece = self.board[self.ep_opposing_pawn_position]

		# modify game board
		self.board[self.original_position] = "EE"
		self.board[self.new_position] = self_piece
		self.board[self.ep_opposing_pawn_position] = "EE"

		for captured_piece in self.pieces[opposing_piece[0]][opposing_piece[1]]:
			if captured_piece.position == self.ep_opposing_pawn_position:
				self.temporary_capture_piece = captured_piece
				self.pieces[opposing_piece[0]][opposing_piece[1]].remove(captured_piece)
				break

		# change position of moved piece
		for piece in self.pieces[self_piece[0]][self_piece[1]]:
			if piece.position == self.original_position:
				piece.position = self.new_position
				return piece