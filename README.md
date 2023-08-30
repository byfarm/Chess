
"# chess"

This is a chess game created from scratch during my time in Auckland, New Zealand. The AI engine is modeled after the AlphaZero algorithm developed by DeepMind in the 2010's. Due to the recources needed to train this algorithm (DeepMind used 500 TPU's over the span of several days), my implementation is not highly rated. That being said, if you would like to play against the engine (which is effectively just a random move generator at this point) you can run the "play_against_neural_network.py" file.

If you and another person would like to play, simply run the "play_against_human.py" file. This pops up a board on the screen. The way to move your pieces is to click on the piece, then click on the square you want to move it to. White moves first!

The game implementation is coded from scratch, will almost all moves available including promotion to queen, castling, and en passant. The only move unavailable is underpromotion. The implementation uses pygame for the display and object oriented programming to create the board and pieces. 

The neural network is modeled after the AlphaZero algorithm developed by DeepMind (https://arxiv.org/pdf/1712.01815.pdf). It uses a policy network to produce a probability vector of the next moves in the position, and a value network to predict the likelihood of winning in that position. These two networks are both used in a monte carlo tree search which semi-randomly selects the next move to explore, then greedily picks the next move to play based on the visit count to that position. 

Please have a look around and if you have any suggestions please let me know!

"# chessr" 
