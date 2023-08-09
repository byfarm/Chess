import pygame
#import rules_and_func.machine_functions as machine_functions


# constants
WIDTH = HEIGHT = 800
ROWS = COLS = 8
SQUARE_SIZE = WIDTH//COLS

# RGB colors
RED = pygame.Color('red')
WHITE = pygame.Color('White')
GREY = pygame.Color('grey')
BLUE = pygame.Color('blue')
FPS = 60
IMAGES = {}


def draw_squares(win: pygame):
	# draws the squares on the board
	win.fill(BLUE)
	for row in range(ROWS):
		for col in range(row % 2, COLS, 2):
			pygame.draw.rect(win, WHITE, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def init_pieces():
	# adds all the pieces for the board
	pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bQ', 'bK', 'bB', 'bN', 'bR', 'bP']
	for piece in pieces:
		IMAGES[piece] = pygame.transform.scale(pygame.image.load(f'C:/Users/bucks/OneDrive/Documents/coding/Python/chess/final_version/images/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(win: pygame, piece_dictionary: dict):
	draw_squares(win)
	for color in piece_dictionary.values():
		for piece_type in color.values():
			for piece in piece_type:
				row, col = piece.position
				win.blit(IMAGES[piece.name], pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def select_color():
	# select color
	hum_color = input('Choose which color you would like to play with (w/b): ')
	if hum_color == 'w':
		turn = 'h'
		return turn
	elif hum_color == 'b':
		turn = 'm'
		return turn
	else:
		return select_color()


def human_move(tree: object, sq_selected: tuple, player_click: list[tuple]):
	# makes a human move
	mv_played = None
	# gets all events in pygame
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			tree.h_node.game.stalemate = True

		# if the event is a mouse press, it records the position and appends it to the click list
		elif event.type == pygame.MOUSEBUTTONDOWN:
			location = pygame.mouse.get_pos()  # x, y of location
			m_col = location[0] // SQUARE_SIZE
			m_row = location[1] // SQUARE_SIZE
			if sq_selected == (m_row, m_col):
				sq_selected = ()
				player_click = []
			else:
				sq_selected = (m_row, m_col)
				player_click.append(sq_selected)

			# if 2 clicks have been made, then trys to make the move
			if len(player_click) == 2:
				mv_played = machine_functions.human_play_move_display(tree, player_click)

	# returns a bool, if T, move played, F, move not played, None, invalid move
	return mv_played


def determine_winner(tree: object):
	# determines the winner of the game and prints to output
	print()
	if tree.h_node.game.white_win:
		print('White Wins')
	elif tree.h_node.game.white_win is False:
		print('Black Wins')
	else:
		print('Game is Draw')