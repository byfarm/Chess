import numpy as np
from rules_and_func.game import MachineBoard
import AI.ai as ai
import AI.ai_MCTS as mcts
import time

policy_network = ai.policy_NN()
value_network = ai.value_NN()


def self_train_game() -> (list[np.ndarray, list[float]], bool):
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

	# find the best move then play it and and important info to exapmles
	while not root_tree.game.stalemate:
		best_node = max(root_tree.child_nodes, key=lambda child: child.number_of_visits)
		examples.append([root_tree.bitboard, root_tree.policy_vector])
		if not root_tree.game.stalemate:
			root_tree = mcts.MCTS(starting_node=best_node)

			# game end checks
			root_tree.game.check_for_checkmate()
			root_tree.game.look_for_draws()
			if len(root_tree.game.legal_moves) == 0:
				break

	return examples


# this function is no longer needed since it updates the value array through backpropogation
def assign_winner(examples: list[np.ndarray, list[float], float, None], white_win: bool) -> list[np.ndarray, list[float], float, None]:
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


def train_ai(results: list[np.ndarray, list[float]], value_net, policy_net):
	"""
	trains then saves the NNs
	:param results: the results from the game
	:param value_net: the value NN
	:param policy_net: the policy NN
	:return:
	"""
	# init new network
	new_policy_net = ai.policy_NN()

	number_of_moves = len(results)
	# split appart the results list
	results_bitboards = []
	results_policies = []
	results_values = []
	results_outcomes = []
	for move in results:
		results_bitboards.append(move[0])
		results_policies.append(move[1])

	# change everything to np arrays
	np_input_bitboards = np.empty((number_of_moves, 14, 8, 8))
	np_label_policies = np.empty((number_of_moves, 218))
	for i in range(number_of_moves):
		np_input_bitboards[i, :, :, :] = results_bitboards[i]
		np_label_policies[i, :] = results_policies[i]

	# train the networks
	new_policy_net.fit(np_input_bitboards, np_label_policies)

	# save the networks
	new_policy_save_path = "AI/neural_networks/policy_new.keras"
	value_save_path = "AI/neural_networks/value.keras"
	policy_save_path = "AI/neural_networks/policy.keras"
	new_policy_net.save(new_policy_save_path)
	value_net.save(value_save_path)
	policy_net.save(policy_save_path)


if __name__ == "__main__":
	start = time.time()
	examples = self_train_game()
	train_ai(examples, value_network, policy_network)
	end = time.time()
	time_elapsed = end - start
	print(f'Time to complete 1 game: {time_elapsed} seconds')




