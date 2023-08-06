import copy
import numpy as np
from ai_train import POLICY_NETWORK, VALUE_NETWORK
import AI.ai as ai
import random
import math


class Game_Node(object):
	"""
	the game node object for each game state
	"""
	def __init__(self, game: object, move: list=None, parent_node: object=None):
		# TODO: the policy vector should include the ucb1 score, the output from the policy NN, and the value evaluation
		# this means do not make the policy vector unless it is a chosed leaf node because then must init all children.
		# make the policy call outside the init method
		"""
		:param game: the game state
		:param move: the move taken to reach this game state
		:param parent_node: the parent node of the game
		bitboard: the 14 layer bitboard of the game state
		value_evaluation: the value of the position from the value NN
		policy_vector: the move probabilities from the policy NN
		number_of_visits: the number of visits the mcts has made to the node
		child_nodes: the child nodes of the game node
		wins: the number of wins from this position
		"""
		self.move = move
		self.game = game
		self.parent_node = parent_node if parent_node else False

		# get the evaluation
		self.bitboard = ai.to_bits(game)
		self.value_evaluation = VALUE_NETWORK.predict(self.bitboard)[0, 0]

		# get the policy vector
		number_possible_moves = len(game.legal_moves)
		self.policy_vector = list(POLICY_NETWORK.predict(self.bitboard)[0, :])
		self.policy_vector_legal_moves = list(self.policy_vector[:number_possible_moves] / sum(self.policy_vector[:number_possible_moves]))

		self.number_of_visits = 0
		self.child_nodes = []
		self.visited_boards = []
		self.wins = 0

	def __repr__(self):
		return f'{self.move}'

	def random_game_simulation(self) -> bool:
		"""
		simulates a game randomly to the end
		:return game.white_win: whether white won the game. False = black won, None = draw
		"""
		game = copy.deepcopy(self.game)
		while len(game.legal_moves) > 0 and not game.stalemate:
			move = random.choice(game.legal_moves)
			game.play_machine_move(move)
			game.look_for_draws()
		game.check_for_checkmate()
		return game.white_win

	def get_ucb1_score(self, exploration_constant: float=1.0) -> float:
		"""
		the UCB1 score of the position from the mcts
		:param exploration_constant: the constant in the equation
		:return ucb1_score: the score from the mcts
		"""
		return self.wins / self.number_of_visits + exploration_constant * math.sqrt(math.log(self.parent_node.number_of_visits) / self.number_of_visits)

	def select_child(self, move_probabilities: list[float]) -> list:
		"""
		takes the move probabilities and returns the move with the highest one
		:param move_probabilities: the output from the policy vector
		:return best_move: the best move based on the policy vector in the position
		"""
		max_value = max(move_probabilities)
		move_index = move_probabilities.index(max_value)
		return self.game.legal_moves[move_index]


def back_propagate(node: object, result: float, leaf_move_turn: str):
	"""
	back propagates through network and updates if white won or not
	:param leaf_move_turn: the color of the leaf node
	:param node: the leaf node object
	:param result: the white_wins result
	:return none
	"""
	while node:
		node.number_of_visits += 1
		if node.game.move_turn == leaf_move_turn:
			if result > 0.75:
				node.wins += 1
		else:
			if result < 0.25:
				node.wins += 1
		node = node.parent_node


def MCTS(game: object=None, starting_node: object=None, iterations: int=2) -> object:
	"""
	the monte carlo tree search from a game position
	:param starting_node: if the tree has already been init, then use this to keep the existing nodes
	:param game: the game state, will be the starting board position that inits the tree
	:param iterations: the number of times you want to search from the root node
	:return best_move: the best move in the position based on the MCTS tree search
	"""
	# check if the tree is already existing
	if starting_node is None:
		root = Game_Node(game)
	else:
		root = starting_node
		game = starting_node.game

	for _ in range(iterations):
		# set variables
		parent_game_node = root
		selected_move = root.select_child(root.policy_vector_legal_moves)
		selected_game_state = copy.deepcopy(game)
		selected_game_state.play_machine_move(selected_move)

		# find if the board has been visited or not
		board_visited = True
		while board_visited:
			# reset if visited
			board_visited = False

			# check if visisted
			for board in enumerate(root.visited_boards):
				if np.array_equal(board[1], selected_game_state.board):
					board_visited = True
					selected_game_node = root.child_nodes[board[0]]
					break

			# if it has been visited then find the next move
			if board_visited:
				selected_move = selected_game_node.select_child(selected_game_node.policy_vector_legal_moves)
				parent_game_node = selected_game_node
				selected_game_state = copy.deepcopy(selected_game_node.game)
				selected_game_state.play_machine_move(selected_move)

		# creates new leaf and back propagates through
		leaf = Game_Node(selected_game_state, move=selected_move, parent_node=parent_game_node)
		root.visited_boards.append(selected_game_state.board)
		root.child_nodes.append(leaf)
		self_win = leaf.value_evaluation
		back_propagate(leaf, self_win, leaf.game.move_turn)

	return root




"""
I need to find the real winning state of the game, backpropogate through the entire tree and assign the result,
then try to fit it with the value netowrk
"""