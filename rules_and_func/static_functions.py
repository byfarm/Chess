
def insert_sort_h_to_l(data: list):
	"""
	sorts data from a list of tuples from h to l. value assumed to be in 0th index of tuple
	:param data: unsorted list of tuple
	:return data: sorted list of tuples
	"""
	for idx in range(1, len(data)):
		while data[idx][0] > data[idx - 1][0] and idx > 0:
			temp = data[idx]
			data[idx] = data[idx - 1]
			data[idx - 1] = temp
			idx -= 1
	vals = []
	objects = []
	for i in data:
		vals.append(i[0])
		objects.append(i[1])
	return vals, objects


def sort_node_scores(tree: object):
	"""
	sorts the scores in the tree from h to low
	:param tree: the game tree
	:return s_scores: list, the sorted scores h to l
	:return s_nodes: list, the sorted nodes h to l
	"""
	# create a score tuple, then sort it high to low
	scores: list = []
	for node in tree.game_nodes:
		score_tup = (node.wins, node)
		scores.append(score_tup)
	s_scores, s_nodes = insert_sort_h_to_l(scores)
	return s_scores, s_nodes


p_vals = {'Q': 9, 'R': 5, 'N': 3, 'B': 3, 'P': 1, 'K': 0}