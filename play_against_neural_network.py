from rules_and_func import machine_functions
import pygame
import rules_and_func.display_functions as df
from rules_and_func.game import MachineBoard
from AI.ai_MCTS import MCTS


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
			print("human's turn")
			legal_move = False
			while not legal_move:
				# loop through the game events
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						root_tree.game.stalemate = True

					# if square pressed, get the location and add it to the moves
					elif event.type == pygame.MOUSEBUTTONDOWN:
						location = pygame.mouse.get_pos()
						m_col = location[0] // df.SQUARE_SIZE
						m_row = location[1] // df.SQUARE_SIZE
						if sq_selected == (m_row, m_col):
							sq_selected = ()
							player_click = []
						else:
							sq_selected = (m_row, m_col)
							player_click.append(sq_selected)

						# if 2 clicks have happened try and play the move
						if len(player_click) == 2:
							legal_move, root_tree = machine_functions.human_move_nn(root_tree, player_click)
							sq_selected = ()
							player_click = []
							turn = 'm'

		# if it is the machine's turn, have the machine find a move and play it
		elif turn == 'm':
			print('caclulating move')
			root_tree = MCTS(starting_node=root_tree)
			root_tree = max(root_tree.child_nodes, key=lambda child: child.number_of_visits)
			print('move played')
			turn = 'h'

		root_tree.game.look_for_draws()
		root_tree.game.check_for_checkmate()

	# find the winner and print the game
	df.determine_winner_nn(root_tree)
	pygame.quit()