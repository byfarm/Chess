import math
import numpy
import rules_and_func.static_functions as sf
import copy


class GameNode(object):
	def __init__(self, move: tuple=None, board: object=None):
		# create a copy of the game
		self.game: object = copy.deepcopy(board)
		self.score: float = 0.0
		self.num_visits: int = 0

		# make it so that there are not too many print statements
		def pb(argument):
			pass

		self.game.print_board = pb

		# move is none means it is the head node
		if move is None:
			self.name: str = "Head"
			self.value = 0
			self.play = None
		else:
			# else the name is the move, value is 0, and play the move
			self.name: tuple = move[0]
			self.value: int = 0
			self.game.play_machine_move(move)
			self.play: tuple = move

		if self.game.move_turn == 'b':
			self.color = 'w'
		else:
			self.color = 'b'
		self.game_stage, self.all_pic, self.all_pic_dic, self.s_pic_dic, self.opp_pic_dic, self.s_pic, self.opp_pic = \
			None, None, None, None, None, None, None


	def __repr__(self):
		return f'{self.name}'

	def calc_score(self, total_lines: int):
		"""
		calculates
		:param total_lines: how many lines have run through the tree
		:return: updates the score value
		"""
		if self.num_visits > 0 and total_lines > 0:
			self.score += (self.value / self.num_visits + 0.1 * (math.log(total_lines)/self.num_visits)**0.5) * 25
		else:
			self.score += 0

	def determ_value(self, white_win: bool):
		"""
		updates the value of wins vs losses vs draws
		:param white_win: whether white won or not
		:return: self.value
		"""
		self.num_visits += 1
		if white_win is None:
			pass
		elif (self.color == 'w' and white_win) or (self.color == 'b' and not white_win):
			self.value += 1
		else:
			self.value -= 1

	def eval_pos(self):
		"""
		updates score for evaluation. looks at the current node's gamestate
		"""
		self.all_pic, self.all_pic_dic, self.s_pic_dic, self.opp_pic_dic, self.s_pic, self.opp_pic = self.find_pieces()
		s_moves, s_check_moves, s_cap = self.game.find_machine_moves(self.color)
		self.game_stage = self.find_gamestage()
		self.piece_mobility(s_moves)
		self.material()
		self.king_pos()
		self.pawn_struct()
		self.opp_cap()
		self.self_cap(s_cap)
		self.checkmate()
		if self.game_stage == 'beg':
			self.opening()

	def find_pieces(self):
		"""
		updates the values for all the piece info for the evaluation functions
		:return:
		"""
		# finds all the pieces on the board and makes a dictionary and a set
		piece_dictionary = {}
		for i in self.game.pieces['b'].keys():
			if i != 'K':
				piece_dictionary[i] = self.game.pieces['b'][i] + self.game.pieces['w'][i]
		pieces_in_play = set(piece_dictionary['Q']).union(
			piece_dictionary['B'],
			piece_dictionary['R'],
			piece_dictionary['N'],
			piece_dictionary['P'])

		# find all the white pieces
		white_pieces = []
		for i in self.game.pieces['w'].keys():
			white_pieces += self.game.pieces['w'].get(i)

		# find all the black pieces
		black_pieces = []
		for i in self.game.pieces['b'].keys():
			black_pieces += self.game.pieces['b'].get(i)

		# assign pieces to node
		if self.color == 'b':
			self_pieces_dic = self.game.pieces['b']
			opp_pieces_dic = self.game.pieces['w']
			self_pic = black_pieces
			opp_pic = white_pieces
		else:
			self_pieces_dic = self.game.pieces['w']
			opp_pieces_dic = self.game.pieces['b']
			self_pic = white_pieces
			opp_pic = black_pieces

		return pieces_in_play, piece_dictionary, self_pieces_dic, opp_pieces_dic, self_pic, opp_pic

	def find_gamestage(self):
		# finds the stage of the game
		tot_points = sum([i.value for i in self.all_pic])
		if tot_points < 25:
			gamestage = 'end'
		elif tot_points < 45:
			gamestage = 'mid'
		else:
			gamestage = 'beg'
		return gamestage

	def castle(self, c=15):
		# checks to see if the last move was a castle. if it was adds a bias to it
		if self.game.move_log[-1][2] is not None:
			if self.game.move_log[-1][2][0] is True:
				self.score += 1*c

	def checkmate(self):
		# checks to see if the current position is checkmate, if is, makes the computer pick it
		self.game.check_for_checkmate()
		if self.game.stalemate is True:
			self.score += numpy.inf

	def material(self, c=5):
		# biases for the material in the position
		mat_diff = sum([p.value for p in self.s_pic]) - sum([p.value for p in self.opp_pic])
		self.score += c*mat_diff

	def piece_mobility(self, moves: list, c=4):
		# if there are more moves, it is a possitive
		self.score += c*len(moves)

	def king_pos(self, c=3):
		# adds bias for king position based on which part of the game
		posi = self.s_pic_dic['K'][0].position

		# if end king needs freedom to move wherever
		if self.game_stage == 'end':
			pass

		# if mid or start, king should try and stay out the middle
		elif self.game_stage == 'mid':
			if posi[0] < 3 or posi[0] > 5:
				self.score += c*1
			if posi[1] < 3 or posi[1] > 5:
				self.score += c*1
		else:
			if posi[0] < 1 or posi[0] > 6:
				self.score += c*1
			if posi[1] < 2 or posi[1] > 6:
				self.score += c*1

	def pawn_struct(self, c=2):
		# analyzes the pawn strucure, takes bias off if there are open files and backward pawns
		board = copy.deepcopy(self.game.board)
		if self.color == 'w':
			board = numpy.rot90(board, 2)

		# finds columns the rooks and pawns are in
		cols = []
		r_cols = []
		for r in range(8):
			if f'{self.color}P' in board[:, r]:
				cols.append(True)
			else:
				cols.append(False)
			if f'{self.color}R' in board[:, r]:
				r_cols.append(True)
			else:
				r_cols.append(False)

		# sees if any pawns are isolated
		for i in range(1, 7):
			if cols[i+1] is False and cols[i+1] is False and cols[i] is True:
				self.score -= 1*c
		if (cols[0] is True and cols[1] is False) or (cols[7] is True and cols[6] is False):
			self.score -= 1*c

		# sees if any rooks are in open files
		for i in range(8):
			if r_cols[i] is True and cols[i] is False:
				self.score += 1*c

		# tries to find backwards pawns
		spaces = None
		for p in range(8):
			if f'{self.color}P' in board[p, :]:
				spaces = list(board[p, :])
				break
		if spaces is not None:
			spaces.remove(f'{self.color}P')
			if f'{self.color}P' not in spaces:
				self.score -= 1*c

	def opening(self, c=1):
		# check to see if king castled
		if self.game.move_counter > 1:
			self.castle()

		# want the pawns in the midde
		pawn_pos = {i.position for i in self.s_pic_dic['P']}
		i_sqs = set()
		for r in range(2, 6):
			for c in range(2, 6):
				i_sqs.add((r, c))
		for k in i_sqs:
			if k not in pawn_pos:
				self.score -= 1*c

		# dont want it to play king pawn
		if self.game.move_log[-1][0] == [(1, 5), (1, 5)] or self.game.move_log[-1][0] == [(6, 5), (5, 5)]:
			self.score -= 10 * c

		# if the move was not a pawn adds a bit
		if self.game.board[self.game.move_log[-1][0][1]][1] != 'P':
			self.score += 3 * c

		if self.game.board[self.game.move_log[-1][0][1]][1] == 'Q':
			self.score -= 20 * c

	def opp_cap(self, c=10):
		# checks to see what the opponent can capture, is proportional to the value of the piece
		opp_cap = self.game.captures
		opp_cap = {i for i in opp_cap if i[0] != 'E'}
		if len(opp_cap) > 0:
			for p in opp_cap:
				self.score -= c*self.s_pic_dic[p[1]][0].value

	def self_cap(self, self_cap, c=3):
		# looks for what self can capture
		self_cap = [i for i in self_cap if i[0] != 'E']
		if len(self_cap) > 0:
			for p in self_cap:
				self.score += c * sf.p_vals[p[1]]


class GamesTree(object):
	def __init__(self, game: object, game_nodes: list=None):
		if game_nodes is None:
			self.game_nodes = []
		self.h_node: object = GameNode(board=game)
		self.total_lines: int = 0

		# find all moves and add them to the tree
		for par_move in self.h_node.game.legal_moves:
			self.add_game_node(par_move, game)

	def __repr__(self):
		game_node_names = '\n'.join(node.__repr__() for node in self.game_nodes)
		return f'{game_node_names}\n'

	def add_game_node(self, move: tuple, board: object):
		"""
		adds a game node to the tree
		:param move: the move ([(5,4),(4,3)], e_pasant, [castleability, rook, spaces])
		:param board: the board object with everything
		:return: updates the networks game nodes
		"""
		node: object = GameNode(move, board)
		# append the new node
		self.game_nodes.append(node)

	def make_a_move(self, play: tuple=None):
		"""
		decides what move to play and makes it
		:return: updates the head node
		"""
		if len(self.game_nodes) == 0:
			self.h_node.game.stalemate = True
		else:
			if play is None:
				# sorts the scores h to low
				scores: list = [(i.score, i.play) for i in self.game_nodes]
				s_scores, s_plays = sf.insert_sort_h_to_l(scores)

				# chooses the best move and plays it
				play: tuple = s_plays[0]

			# update the current h_node
			for i in self.game_nodes:
				if i.play == play:
					self.h_node = i
					break
			self.game_nodes = []

			# add all the new moves to game nodes
			for i in self.h_node.game.legal_moves:
				self.add_game_node(i, self.h_node.game)
