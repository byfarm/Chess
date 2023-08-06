import numpy as np
from rules_and_func.game import MachineBoard
import AI.ai as ai
import AI.ai_MCTS as mcts



policy_network = ai.policy_NN()
value_network = ai.value_NN()


def self_train_game() -> list[np.ndarray, list[float], float, None]:
	"""
	has the ai play against itself
	:return:
	"""
	# init games
	game = MachineBoard()
	examples = []
	root_tree = mcts.MCTS(game)
	while not root_tree.game.stalemate:
		best_node = max(root_tree.child_nodes, key=lambda child: child.get_ucb1_score())
		examples.append([root_tree.bitboard, root_tree.policy_vector, best_node.value_evaluation, None])
		if not root_tree.game.stalemate:
			root_tree = mcts.MCTS(starting_node=best_node)

	return examples, root_tree.game.white_win


def assign_winner(examples, white_win):
	if white_win:
		white_addition = 1.0
		black_addition = 0.0
	elif white_win is False:
		white_addition = 0.0
		black_addition = 1.0
	else:
		white_addition = 0.5
		black_addition = white_addition

	for move_index in range(len(examples)):
		if move_index % 2 == 1:
			examples[move_index][-1] = white_addition
		else:
			examples[move_index][-1] = black_addition
	return examples


def train_ai(results: list[np.ndarray, list[float], float, float], value_net):
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
		results_values.append(move[2])
		results_outcomes.append(move[3])

	# change everything to np arrays
	np_input_bitboards = np.empty((number_of_moves, 14, 8, 8))
	np_label_policies = np.empty((number_of_moves, 218))
	np_label_outcomes = np.array(results_outcomes)
	np_input_values = np.array(results_values)
	for i in range(number_of_moves):
		np_input_bitboards[i, :, :, :] = results_bitboards[i]
		np_label_policies[i, :] = results_policies[i]

	# train the networks
	new_policy_net.fit(np_input_bitboards, np_label_policies)
	value_net.fit(np_input_bitboards, np_label_outcomes)

	new_policy_save_path = "neural_networks/policy_new.keras"
	value_save_path = "neural_networks/value.keras"
	new_policy_net.save(new_policy_save_path)
	value_net.save(value_save_path)





if __name__ == "__main__":
	examples, white_win = self_train_game()
	examples_with_result = assign_winner(examples, white_win)




