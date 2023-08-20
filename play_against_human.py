from rules_and_func import machine_functions
from rules_and_func.game import *
from rules_and_func.monte_carlo import *
from rules_and_func.display_functions import *



def main():
	# initialize game
	WIN = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption('Chess')

	# initialize game
	clock = pygame.time.Clock()
	init_pieces()
	game = MachineBoard()
	tree = GamesTree(game)

	# loop through while game is still running
	sq_selected = ()
	player_click = []
	while not tree.h_node.game.stalemate:

		# update the game board
		clock.tick(FPS)
		draw_pieces(WIN, tree.h_node.game.pieces)
		pygame.display.update()

		# loop through the game events
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				tree.h_node.game.stalemate = True

			# if square pressed, get the location and add it to the moves
			elif event.type == pygame.MOUSEBUTTONDOWN:
				location = pygame.mouse.get_pos()
				m_col = location[0]//SQUARE_SIZE
				m_row = location[1]//SQUARE_SIZE
				if sq_selected == (m_row, m_col):
					sq_selected = ()
					player_click = []
				else:
					sq_selected = (m_row, m_col)
					player_click.append(sq_selected)

				# if 2 clicks have happened try and play the move
				if len(player_click) == 2:
					machine_functions.human_play_move_display(tree, player_click)
					sq_selected = ()
					player_click = []
		tree.h_node.game.check_for_checkmate()
	# find the winner then end the game

	determine_winner(tree)
	pygame.quit()


if __name__ == '__main__':
	main()