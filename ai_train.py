import numpy as np
from rules_and_func.game import MachineBoard
import AI.ai as ai
import time
import tensorflow as tf
import pygame
import AI.ai_MCTS as mcts
from rules_and_func.display_functions import draw_pieces, WIDTH, HEIGHT, init_pieces
import AI.neural_networks as nn
import pandas as pd


"""
try:
	# POLICY_NETWORK = keras.models.load_model(NEW_POLICY_SAVE_PATH)
	# VALUE_NETWORK = keras.models.load_model(VALUE_SAVE_PATH)
	POLICY_NETWORK = ai.policy_NN()
	VALUE_NETWORK = ai.value_NN()
except OSError:
	POLICY_NETWORK = ai.policy_NN()
	VALUE_NETWORK = ai.value_NN()
"""


def self_train_game() -> (list[np.ndarray, list[float], None], bool):
	"""
	has the ai play against itself
	:return examples: [bitboard, policy vector, evaluation, none] of move/board
	:return white_win: whether white won the game
	"""
	# init games
	game = MachineBoard()

	# init the MCTS and get the tree
	examples = []
	root_tree = mcts.MCTS(game)

	# find the best move then play it and important info to exapmles
	move = 0
	while not root_tree.game.stalemate:

		examples.append([root_tree.bitboard, root_tree.policy_vector, None])
		root_tree.game.look_for_draws()
		root_tree.game.check_for_checkmate()
		if not root_tree.game.stalemate:
			# best_node = max(root_tree.child_nodes, key=lambda child: child.number_of_visits)
			best_node = root_tree.select_child(root_tree.policy_vector_legal_moves)
			root_tree = mcts.MCTS(starting_node=best_node)
			move += 1
			print(f"\nmade move number: {move}")

	print("game over")
	return examples, root_tree.game.white_win


def assign_winner(examples: list[np.ndarray, list[float], None], white_win: bool) -> list[np.ndarray, list[float], float]:
	"""
	assigns the winner based on if white won or not
	:param examples: the info from each move in the game
	:param white_win: whether white won the game or not. None is draw
	:return examples: the examples updated with the win value
	"""
	# find the win value
	if white_win:
		white_addition: float = 1.0
		black_addition: float = 0.0
	elif white_win is False:
		white_addition: float = 0.0
		black_addition: float = 1.0
	else:
		white_addition: float = 0.5
		black_addition: float = white_addition

	# add the win value to the end of the example
	for move_index in range(len(examples)):
		if move_index % 2 == 1:
			examples[move_index][-1]: float = white_addition
		else:
			examples[move_index][-1]: float = black_addition
	return examples


def train_ai(results: list[np.ndarray, list[float], float]):
	"""
	trains then saves the NNs
	:param results: the results from the game
	:return value_net: the value NN
	:return policy_net: the policy NN
	"""
	# init new network
	new_policy_net = nn.policy_NN()
	new_value_net = nn.value_NN()

	# split apart the results list
	results_bitboards = []
	results_policies = []
	results_outcomes = []
	for move in results:
		results_bitboards.append(move[0])
		results_policies.append(move[1])
		results_outcomes.append(move[2])

	# change outcomes to tf
	tf_input_bitboards = tf.concat(results_bitboards, axis=0)
	tf_label_policies = tf.stack(results_policies)
	tf_label_outcomes = tf.constant(results_outcomes)

	# train the networks
	new_policy_net.fit(tf_input_bitboards, tf_label_policies)
	new_value_net.fit(tf_input_bitboards, tf_label_outcomes)

	print(tf_label_outcomes.numpy()[0], len(results_outcomes))
	return new_policy_net, new_value_net


def view_train_game() -> (list[np.ndarray, list[float], None], bool):
	"""
	has the ai play against itself with pygame board viewing enabled
	:return examples: [bitboard, policy vector, evaluation, none] of move/board
	:return white_win: whether white won the game
	"""
	WIN = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption('Chess')
	init_pieces()
	# init games
	game = MachineBoard()

	# init the MCTS and get the tree
	examples = []
	root_tree = mcts.MCTS(game)

	# find the best move then play it and important info to exapmles
	move = 0
	while not root_tree.game.stalemate:
		pygame.event.get()
		draw_pieces(WIN, root_tree.game.pieces)
		pygame.display.update()

		examples.append([root_tree.bitboard, root_tree.policy_vector, None])
		root_tree.game.look_for_draws()
		root_tree.game.check_for_checkmate()
		if not root_tree.game.stalemate:
			# best_node = max(root_tree.child_nodes, key=lambda child: child.number_of_visits)
			best_node = root_tree.select_child(root_tree.policy_vector_legal_moves)
			root_tree = mcts.MCTS(starting_node=best_node)
			move += 1
			print(f"\nmade move number: {move}", root_tree)

	print("game over")

	# pygame.quit()
	return examples, root_tree.game.white_win

def write_data_to_csv(examples: list):
	df = pd.DataFrame(examples)
	df.to_csv("training_data.csv")

def load_csv_data(path: str):
	df = pd.read_csv(path)
	return list(df)


def train_one_network():
	# todo: implement it so it can train and verify
	# load the previous networks
	save_addresses = nn.init_network_paths()
	while True:
		examples, white_win = view_train_game()
		examples_with_result = assign_winner(examples, white_win)
		new_policy_network, new_value_network = train_ai(examples_with_result)
		nn.save_model(new_value_network, new_policy_network, nn.VALUE_NETWORK, nn.POLICY_NETWORK, save_addresses)





if __name__ == "__main__":
	start = time.time()

	train_one_network()

	end = time.time()
	time_elapsed = end - start
	print(f"\nTime elapsed: {time_elapsed} seconds\n")




