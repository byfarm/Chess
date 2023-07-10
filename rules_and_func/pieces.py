import rules_and_func.static_functions as sf


class Pawn:
	def __init__(self, name, position):
		"""
		:param name: str
			first letter color, second piece type
		:param position: tupple
			row, column of position
		"""
		# initialize color, whether piece has moved, and position on the board
		self.name = name
		self.color = name[0]
		self.moved = False
		self.position = position
		self.value = 1

	def check_legal_move(self, desire_move, board):
		"""
		check to see if the desired move is legal.
		:param desire_move: tupple of ints
			coordinates of desired move (row, column)
		:param board: 2d list
			map of current board
		:return legality: bool
			whether move is legal or not
		Notes:
			preconditions:
				will be a move, not a capture
				checks will be from another definition

		"""
		# spaces the pawn is moving through
		spaces = []
		# initialize legality
		legality = False

		# define the relevant spaces that the pawn will move through
		spaces_moved = desire_move[0] - self.position[0]
		# make sure pawn can only move forward
		if (self.color == 'w' and spaces_moved > 0) or (self.color == 'b' and spaces_moved < 0):
			pass
			# make sure pawn can only move forward
		if (self.color == 'w' and spaces_moved > 0) or (self.color == 'b' and spaces_moved < 0):
			pass
		elif spaces_moved > 0:
			# go through all spaces the pawn is moving through on the board and append into a list
			for i in range(0, spaces_moved + 1):
				n = board[self.position[0] + i, self.position[1]]
				spaces.append(n)
				if len(spaces) == abs(spaces_moved) + 1:
					break
		else:
			for i in range(spaces_moved, 1):
				n = board[self.position[0] + i, self.position[1]]
				spaces.append(n)
				if len(spaces) == abs(spaces_moved) + 1:
					break
		# check to make sure desire move and current position have same column and dont have same square
		if desire_move[1] != self.position[1] or desire_move == self.position:
			pass

		# if pawn has not moved, check to make sure that if it moves 2 or 1 space, the spaces are empty
		elif self.moved is False:
			if abs(spaces_moved) <= 2:
				if (spaces == [self.name] + ['EE'] * abs(spaces_moved)) or spaces == ['EE'] * abs(spaces_moved) + [self.name]:
					legality = True

		# if pawn has moved, make sure the one space is empty
		elif self.moved is True:
			if abs(spaces_moved) == 1:
				if spaces == [self.name, 'EE'] or spaces == ['EE', self.name]:
					legality = True

		# return legality
		return legality

	def capture(self, desired_capture, board, move_log):
		"""
		captures another piece
		:param desired_capture: tupple
			space that you want to capture
		:param board: board
			current game board
		:param move_log: list
			log of past moves ex: ['Pe6,Pe7', ... ] (reads: pawn on e6 to pawn on e7)
		:return legality_cap: bool
			whether you can capture or not
		:return piece: str
			str of what you are captureing
		:return e_passant: bool
			whether e_passant was used or not
		Notes:
			PRE:
				will be defined as capture beforehand

		"""
		# initialize variables
		piece = 'EE'
		legality_cap = False
		e_passant = False
		# cap piece will be str ex: 'bN'
		cap_piece = board[desired_capture]

		# cap piece cannot be of the same color, or on the same square
		if cap_piece[0] == self.color or desired_capture == self.position:
			pass
		# cap piece must be in adjacent colums to pawn
		elif abs(desired_capture[1] - self.position[1]) == 1:
			# must be in one row up
			row_diff = desired_capture[0] - self.position[0]
			if ((self.color == 'b' and row_diff == 1) or (self.color == 'w' and row_diff == -1)) and cap_piece != 'EE':
				piece = cap_piece
				legality_cap = True
			# if not row up, check for ean passant
			elif cap_piece == 'EE':
				if len(move_log) >= 1:
					last_move = move_log[-1][0]
					first, last = last_move[0], last_move[1]
					p = board[last][1]
					row = first[0]
					end_row = last[0]
					column = last[1]

					# conditions:
					# piece is true
					a = p == 'P'
					# their last move was a double pawn move
					b = abs(row-end_row) == 2
					# capture space is one behind
					c = abs(desired_capture[0] - end_row) == 1
					# they are level with you
					d = end_row == self.position[0]
					# they are on the column next to you
					e = abs(self.position[1] - column) == 1
					# must be capuring pawn whose next to it
					if a and b and c and d and e:
						if self.color == 'w':
							piece = 'bP'
						else:
							piece = 'wP'
						legality_cap = True
						e_passant = True

		return legality_cap, piece, e_passant

	def promotion(self, game, piece_chosen):
		"""
		promotes a piece
		:param game: object
			the state of the game currently being played
		:param piece_chosen: str
			'R' letter of the piece chosen
		Notes:
			precondition: pawn must be on last rank
		"""
		piece_dictionary = game.pieces[self.color]
		name = None
		promoted = False
		while promoted is False:
			# create piece list and have user input what piece they would like to promote to
			pieces = {'Q', 'R', 'B', 'N'}

			# check if piece chosen is in pieces then initialize a single piece of user choice
			if piece_chosen in pieces:
				name = f'{self.color}{piece_chosen}'
				position = self.position
				game.initialize_single_piece(name, position)

				# if promoted to rook make sure castling condition is flipped
				if name == f'{self.color}R':
					for i in piece_dictionary['R']:
						i.moved = True

				# go throught the game's pawns and delete the one that has been promoted
				for i in piece_dictionary['P']:
					if i.position == self.position:
						piece_dictionary['P'].remove(i)
				promoted = True
			else:
				print("Invalid piece, try again")
		return name


class Knight:
	def __init__(self, name, position):
		self.name = name
		self.color = name[0]
		self.position = position
		self.value = 3

	def check_legal_move(self, desire_move, board):
		"""
		checks legality of selected move
		:param desire_move: tupple of ints
			desired move (row, column)
		:param board: 2d np array
			current board state
		:return legality: bool
			whether move is legal or not
		:return cap_piece: str
			str 'bB' of captured piece or 'EE'
		"""
		legality = False
		desire_space = board[desire_move]

		# find slope for diagonal check
		run = desire_move[0] - self.position[0]
		rise = desire_move[1] - self.position[1]
		# dont get a divide by zero error
		if abs(rise) == abs(run) and run != 0:
			m = rise / run
		else:
			m = 0

		# check r to be 3
		lateral = abs(desire_move[1] - self.position[1])
		verticle = abs(desire_move[0] - self.position[0])

		# if it r > 2 or if it is moving to the same space it is on
		if lateral > 2 or verticle > 2 or desire_move == self.position:
			pass

		# check that move is not in same row or column
		elif desire_move[0] == self.position[0] or desire_move[1] == self.position[1]:
			pass

		# check to make sure is an L not diagonal
		elif abs(m) == 1:
			pass

		# check to see if starting square is same as ending square
		elif desire_move == self.position:
			pass
		# check that not capturing own piece
		elif desire_space[0] == self.color:
			pass
		# else move is good
		else:
			legality = True

		return legality, desire_space


class Bishop:
	def __init__(self, name, position):
		self.name = name
		self.color = name[0]
		self.position = position
		self.value = 3

	def check_legal_move(self, desire_move, board):
		"""
		checks legality of selected move
		:param desire_move: tupple of ints
			desired move (row, column)
		:param board: 2d np array
			current board state
		:return legality: bool
			whether move is legal or not
		"""
		legality = False
		desire_space = board[desire_move]
		spaces = []

		diff_row = desire_move[0] - self.position[0]
		diff_column = desire_move[1] - self.position[1]

		# if on a diagonal
		if abs(diff_row) == abs(diff_column) and diff_row != 0:
			# the slope of the change must be 1 or -1, and the space to move to must be opposite color or empty
			m = diff_row/diff_column
			# if capturing a piece of the same color or the desired move is same space as piece already is
			if desire_space[0] == self.color or self.position == desire_move:
				pass
			# if slope is positive, will go up one over one
			elif m > 0:
				if diff_row > 0:
					for i in range(0, diff_row + 1):
						spaces.append(board[(self.position[0] + i, self.position[1] + i)])
				else:
					for i in range(0, diff_row - 1, -1):
						n = board[(self.position[0] + i, self.position[1] + i)]
						spaces.append(n)

			# if slope is negative, will go down one over one
			elif m < 0:
				if diff_column > 0:
					for i in range(0, diff_column + 1):
						n = board[self.position[0] - i, self.position[1] + i]
						spaces.append(n)
				else:
					for i in range(0, diff_row + 1):
						n = board[self.position[0] + i, self.position[1] - i]
						spaces.append(n)

			# check to make sure 0 space is the piece and all other spaces are empty
			legal_spaces = [f'{self.color}B'] + ['EE'] * (abs(diff_row) - 1) + [desire_space]
			if spaces == legal_spaces and diff_row != 0:
				legality = True

		return legality, desire_space


class Rook:
	def __init__(self, name, position):
		self.name = name
		self.color = name[0]
		self.position = position
		self.moved = False
		self.value = 5

	def check_legal_move(self, desired_move, board):
		"""
		checks legality of selected move
		:param desired_move: tupple of ints
			desired move (row, column)
		:param board: 2d np array
			current board state
		:return legality: bool
			whether move is legal or not
		:return captured_piece: str
			piece that is captured if one is
		"""
		legality = False
		desire_space = board[desired_move]
		spaces = []
		spaces_moved = 0
		# check either row or column must be == and cannot equal same color and cannot be exact same space
		if desire_space[0] == self.color or desired_move == self.position:
			pass

		# if rows are equal
		elif desired_move[0] == self.position[0]:
			# spaces moved determine the expected 'EE' for our spaces list
			spaces_moved = desired_move[1] - self.position[1]
			# appends all spaces from the board moved through into the spaces list
			if spaces_moved > 0:
				for i in range(0, spaces_moved+1):
					n = board[self.position[0], self.position[1] + i]
					spaces.append(n)
			else:
				for i in range(0, spaces_moved-1, -1):
					n = board[self.position[0], self.position[1] + i]
					spaces.append(n)

		# if columns are equal
		elif desired_move[1] == self.position[1]:
			spaces_moved = desired_move[0] - self.position[0]
			if spaces_moved > 0:
				for i in range(0, spaces_moved + 1):
					spaces.append(board[self.position[0] + i, self.position[1]])
			else:
				for i in range(0, spaces_moved-1, -1):
					spaces.append(board[self.position[0] + i, self.position[1]])
		else:
			# if passes none of these tests then is not a legal move
			pass

		# check to make sure spaces moving through are empty
		legal_spaces = [f'{self.color}R'] + ['EE'] * (abs(spaces_moved) - 1) + [desire_space]
		if spaces == legal_spaces and spaces_moved != 0:
			legality = True

		return legality, desire_space


class Queen:
	def __init__(self, name, position):
		self.name = name
		self.color = name[0]
		self.position = position
		self.value = 9

	def check_legal_move(self, desired_move, board):
		"""
		checks legality of selected move
		:param desired_move: tupple of ints
			desired move (row, column)
		:param board: 2d np array
			current board state
		:return legality: bool
			whether move is legal or not
		:return captured_piece: str
			piece that is captured if one is
		"""
		legality = False
		desire_space = board[desired_move]
		spaces = []

		num_spaces = 0
		# check cannot equal same color
		if desire_space[0] == self.color or desired_move == self.position:
			pass
		### --------------------- Rook Movements ---------------------------------
		# if rows are equal
		elif desired_move[0] == self.position[0]:
			# spaces moved determine the expected 'EE' for our spaces list
			spaces_moved = desired_move[1] - self.position[1]
			num_spaces = abs(spaces_moved)
			# appends all spaces from the board moved through into the spaces list
			if spaces_moved > 0:
				for i in range(0, spaces_moved+1):
					spaces.append(board[self.position[0], self.position[1] + i])
			else:
				for i in range(0, spaces_moved-1, -1):
					spaces.append(board[self.position[0], self.position[1] + i])

		# if columns are equal
		elif desired_move[1] == self.position[1]:
			spaces_moved = desired_move[0] - self.position[0]
			num_spaces = abs(spaces_moved)
			if spaces_moved > 0:
				for i in range(0, spaces_moved+1):
					spaces.append(board[self.position[0] + i, self.position[1]])
			else:
				for i in range(0, spaces_moved-1, -1):
					spaces.append(board[self.position[0] + i, self.position[1]])
		# if does not meet rook movements, must be a bishop movement

		### ------------------------ Bishop Movements --------------------------
		else:
			diff_row = desired_move[0] - self.position[0]
			diff_column = desired_move[1] - self.position[1]
			m = diff_row / diff_column
			num_spaces = abs(diff_row)
			if abs(m) != 1.0:
				pass

			# if slope is positive, will go up one over one
			elif m > 0:
				if diff_row > 0:
					for i in range(0, diff_row + 1):
						spaces.append(board[(self.position[0] + i, self.position[1] + i)])
				else:
					for i in range(0, diff_row - 1, -1):
						n = board[(self.position[0] + i, self.position[1] + i)]
						spaces.append(n)

			# if slope is negative, will go down one over one
			elif m < 0:
				if diff_column > 0:
					for i in range(0, diff_column + 1):
						n = board[self.position[0] - i, self.position[1] + i]
						spaces.append(n)
				else:
					for i in range(0, diff_row + 1):
						n = board[self.position[0] + i, self.position[1] - i]
						spaces.append(n)

			### ------------------ spaces check -------------------------
		# check to see that all spaces are empty
		legal_spaces = [f'{self.color}Q'] + ['EE'] * (num_spaces - 1) + [desire_space]
		if spaces == legal_spaces and num_spaces != 0:
			legality = True

		return legality, desire_space


class King:
	def __init__(self, name, position):
		self.moved = False
		self.name = name
		self.color = name[0]
		self.position = position
		self.in_check = False
		self.value = 0

	def check_legal_move(self, desired_move, board):
		"""
		checks legality of selected move
		:param desired_move: tupple of ints
			desired move (row, column)
		:param board: 2d np array
			current board state
		:return legality: bool
			whether move is legal or not
		:return captured_piece: str
			piece that is captured if one is
		"""
		# initialize outputs
		legality = False
		desire_space = board[desired_move]

		# check that radius is 1 or if it is trying to move to same position it is at
		lateral = desired_move[1] - self.position[1]
		verticle = desired_move[0] - self.position[0]
		if abs(lateral) > 1 or abs(verticle) > 1 or desired_move == self.position:
			pass

		# check not capturing piece of same color
		elif desire_space[0] != self.color:
			legality = True

		return legality, desire_space