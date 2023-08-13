from rules_and_func.game import *
import random
import rules_and_func.static_functions as sf
from pathos.pools import ProcessPool


def run_to_end(node: object, depth: int):
	"""
	runs through end and returns if white won or lost
	:param node: the current node being played on
	:param depth: the depth you want the engine to play till
	:return updates the node's value
	"""
	game: object = copy.deepcopy(node.game)
	curr_move_num: int = copy.deepcopy(game.move_counter)
	max_move: int = curr_move_num + depth
	decsive_pos = None

	# when the game is not over
	while game.stalemate is False and game.move_counter < max_move:
		# play one move
		play_one_rand(game)
		# check that no stalemate or checkmate has happened
		if game.move_counter > 2:
			game.look_for_draws()
			game.check_for_checkmate()

		# if stalemate false, check if it is a decisive position
		if game.stalemate is False:
			decsive_pos = game.eff_end()
			if type(decsive_pos) is bool:
				# run ahead 4 moves and make sure it is still deciscve

				for i in range(4):
					if game.stalemate is False:
						play_one_rand(game)
						game.look_for_draws()
						game.check_for_checkmate()

				decsive_pos = game.eff_end()
				# if game is still in a decisive position then exit loop
				if type(decsive_pos) is bool:
					break

	# once game is over, return who won and the node. If the game was actually won, will return stalemate
	if type(decsive_pos) is bool:
		result = decsive_pos
	else:
		# if game not won, will return the position eval. if position not decisive, will return None
		result = game.white_win

	return result


def play_one_rand(game: object):
	move = move_selection_rand(game.legal_moves)
	game.play_machine_move(move)


def move_selection_rand(pos_moves: list[tuple]):
	"""
	selects the move randomly
	:param pos_moves: list of all possible moves
	:return move: the move selected
	"""
	move_idx = random.randint(0, len(pos_moves) - 1)
	move = pos_moves[move_idx]
	return move


def human_play_move_display(tree: object, move: list[tuple]):
	"""
	checks to see if the move is valid then plays the move
	:param tree: the mc object, used to make the move
	:param move: the input move from the human
	:return:
	"""
	in_mach_move = None
	game = tree.h_node.game

	for i in game.legal_moves:
		if i[0] == move:
			in_mach_move = i
			break

	if in_mach_move is not None:
		tree.make_a_move(in_mach_move)
		print('Human move made')
		return True
	else:
		print('Invalid move, try again')
		return False

def human_move_nn(root_tree: object, move: list[tuple]):
	"""
		checks to see if the move is valid then plays the move
		:param tree: the mc object, used to make the move
		:param move: the input move from the human
		:return:
		"""
	in_mach_move = None
	game = root_tree.game

	for i in game.legal_moves:
		if i[0] == move:
			in_mach_move = i
			break

	if in_mach_move is not None:
		node_moved_to = root_tree.make_a_move(in_mach_move)
		print('Human move made')
		return True, node_moved_to
	else:
		print('Invalid move, try again')
		return False, root_tree

def move_selection_mc(tree: object, num_threads: int=1):
	"""
	selects a move using Monte Carlo Method
	:param num_threads: how many moves you want to return
	:param tree: the tree structure
	:return sel_move: the node being moved
	"""
	moves = []

	# sort the scores in the tree
	s_scores, s_nodes = sf.sort_node_scores(tree)

	# chose the node with the highest score, add it to the moves, recacalulate its score, then select another move
	if len(s_scores) < num_threads:
		num_threads = len(s_scores)

	for p in range(num_threads):
			move = s_nodes.pop(0)
			moves.append(move)
	return moves


def parallel_run(tree: object, branches: int, depth: int):
	"""
	parallelizes the mc method for speed
	:param tree: the tree object
	:param branches: the number of games you want searched at once
	:param depth: the max depth you want it to search to
	:return result: T/F/N of the game result
	:return nodes: the nodes that were played
	"""
	nodes = move_selection_mc(tree, branches)
	tree.total_lines += branches

	# make the depth iterable
	depth_lis = np.repeat(depth, branches)

	with ProcessPool() as pool:
		result = list(pool.imap(run_to_end, nodes, depth_lis))

	return result, nodes


def update_vals(results: list, nodes: list):
	"""
	calculate the max score and the value of each node
	:param results: list of bools
	:param nodes: list of the node objects
	:return: updates the values of the nodes
	"""
	for i in range(len(nodes)):
		node = nodes[i]
		node.determ_value(results[i])


def play_a_mc_move(tree: object, max_depth: int=40, its: int=3, branches: int = 9):
	"""
	plays a move using only the monte carlo method
	:param branches: the number of games you want it searching at once
	:param its: number of iterations through
	:param tree: the tree object of the mc game
	:param max_depth: the max depth you want the game to run to
	"""
	# uncomment if want to use mc method
	for _ in range(its):
		# run through the parallel run
		result, nodes = parallel_run(tree, branches, max_depth)
		# update the values
		update_vals(result, nodes)
		# update the scores
		for node in nodes:
			node.calc_score(tree.total_lines)

	# make the top move
	tree.make_a_move()


