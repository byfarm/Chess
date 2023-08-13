import AI.ai
import pygame
import rules_and_func.display_functions as df
from rules_and_func.game import MachineBoard
from AI.ai_MCTS import MCTS
import ai_train

if __name__ == "__main__":
	# TODO: not registering clicks
	# select color and init game
	turn = df.select_color()
	WIN = pygame.display.set_mode((df.WIDTH, df.HEIGHT))
	pygame.display.set_caption('Chess')
	clock = pygame.time.Clock()
	df.init_pieces()

	# create the game
	game = MachineBoard()
	root_tree = MCTS(game)

	sq_selected = () 	# (r, c)
	player_click = []
	# while game is playing, draw the gamestate and update the display
	while not root_tree.game.stalemate:
		pygame.event.get()
		df.draw_pieces(WIN, root_tree.game.pieces)
		pygame.display.update()
		clock.tick(df.FPS)

		# if it is the human turn, play move. if move is played then reset the clicks, if not, cycle through
		if turn == 'h':
			print("Human move")
			legal_move, root_tree = df.human_move_nn_display(root_tree, sq_selected, player_click)
			df.draw_pieces(WIN, root_tree.game.pieces)
			pygame.display.update()
			if legal_move:
				turn = 'm'
				sq_selected = ()
				player_click = []
			elif not legal_move:
				sq_selected = ()
				player_click = []

		# if it is the machine's turn, have the machine find a move and play it
		elif turn == 'm':
			print('caclulating move')
			best_node = max(root_tree.child_nodes, key=lambda child: child.number_of_visits)
			root_tree = MCTS(starting_node=root_tree)
			print('move played')
			turn = 'h'

		root_tree.game.look_for_draws()
		root_tree.game.check_for_checkmate()

	# find the winner and print the game
	df.determine_winner_nn(root_tree)
	pygame.quit()