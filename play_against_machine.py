from rules_and_func.game import *
from rules_and_func.monte_carlo import *
from rules_and_func.display_functions import *


def main():
	# select color and init game
	turn = select_color()
	WIN = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption('Chess')
	clock = pygame.time.Clock()
	init_pieces()

	# create the game
	game = MachineBoard()
	tree = GamesTree(game)

	sq_selected = () 	# (r, c)
	player_click = []
	# while game is playing, draw the gamestate and update the display
	while not tree.h_node.game.stalemate:
		draw_pieces(WIN, tree.h_node.game.board)
		pygame.display.update()
		clock.tick(FPS)

		# if it is the human turn, play move. if move is played then reset the clicks, if not, cycle through
		if turn == 'h':
			mv_played = human_move(tree, sq_selected, player_click)
			draw_pieces(WIN, tree.h_node.game.board)
			pygame.display.update()
			if mv_played:
				turn = 'm'
				sq_selected = ()
				player_click = []
			elif mv_played is False:
				sq_selected = ()
				player_click = []

		# if it is the machine's turn, have the machine find a move and play it
		elif turn == 'm':
			print('caclulating move')
			for i in tree.game_nodes:
				i.eval_pos()
			machine_functions.play_a_mc_move(tree, max_depth=20, its=2, branches=7)
			print('move played')
			turn = 'h'

		tree.h_node.game.check_for_checkmate()

	# find the winner and print the game
	determine_winner(tree)
	pygame.quit()


if __name__ == '__main__':
	main()
