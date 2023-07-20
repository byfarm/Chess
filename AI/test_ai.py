import pytest
import to_bits
import rules_and_func.game


def test_bits():
	game = rules_and_func.game.MachineBoard()
	bitboard = to_bits.to_bits(game)
	assert bitboard.shape == (14, 8, 8)