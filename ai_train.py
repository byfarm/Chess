import keras.models
import numpy as np
from rules_and_func.game import MachineBoard
import AI.ai as ai
import AI.ai_MCTS as mcts
import time

# load the previous networks
NEW_POLICY_SAVE_PATH = "AI/neural_networks/policy_new.keras"
VALUE_SAVE_PATH = "AI/neural_networks/value.keras"
POLICY_SAVE_PATH = "AI/neural_networks/policy.keras"
try:
	POLICY_NETWORK = keras.models.load_model(NEW_POLICY_SAVE_PATH)
	VALUE_NETWORK = keras.models.load_model(VALUE_SAVE_PATH)
except OSError:
	POLICY_NETWORK = ai.policy_NN()
	VALUE_NETWORK = ai.value_NN()


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
	root_tree = mcts.mcts_improved(game)

	# find the best move then play it and important info to exapmles
	while not root_tree.game.stalemate:

		examples.append([root_tree.bitboard, root_tree.policy_vector, None])
		root_tree.game.look_for_draws()
		root_tree.game.check_for_checkmate()
		if len(root_tree.game.legal_moves) == 0:
			break
		if not root_tree.game.stalemate:
			best_node = root_tree.select_child(root_tree.policy_vector_legal_moves)
			root_tree = mcts.mcts_improved(starting_node=best_node)
			print("\nmade move")

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
		white_addition = 1.0
		black_addition = 0.0
	elif white_win is False:
		white_addition = 0.0
		black_addition = 1.0
	else:
		white_addition = 0.5
		black_addition = white_addition

	# add the win value to the end of the example
	for move_index in range(len(examples)):
		if move_index % 2 == 1:
			examples[move_index][-1] = white_addition
		else:
			examples[move_index][-1] = black_addition
	return examples


def train_ai(results: list[np.ndarray, list[float], float], value_net, policy_net):
	"""
	trains then saves the NNs
	:param results: the results from the game
	:param value_net: the value NN
	:param policy_net: the policy NN
	:return:
	"""
	# init new network
	new_policy_net = ai.policy_NN()

	# data prep
	number_of_moves = len(results)
	# split appart the results list
	results_bitboards = []
	results_policies = []
	results_outcomes = []
	for move in results:
		results_bitboards.append(move[0])
		results_policies.append(move[1])
		results_outcomes.append(move[2])

	# change everything to np arrays
	np_input_bitboards = np.empty((number_of_moves, 14, 8, 8))
	np_label_policies = np.empty((number_of_moves, 218))
	np_label_outcomes = np.array(results_outcomes)
	for i in range(number_of_moves):
		np_input_bitboards[i, :, :, :] = results_bitboards[i]
		np_label_policies[i, :] = results_policies[i]

	# train the networks
	new_policy_net.fit(np_input_bitboards, np_label_policies)
	value_net.fit(np_input_bitboards, np_label_outcomes)

	# save the networks
	new_policy_net.save(NEW_POLICY_SAVE_PATH)
	value_net.save(VALUE_SAVE_PATH)
	policy_net.save(POLICY_SAVE_PATH)

	print(np_label_outcomes)


if __name__ == "__main__":
	start = time.time()

	examples, white_win = self_train_game()
	examples_with_result = assign_winner(examples, white_win)
	train_ai(examples_with_result, VALUE_NETWORK, POLICY_NETWORK)

	end = time.time()
	time_elapsed = end - start
	print(f"\nTime elapsed: {time_elapsed} seconds\n")




