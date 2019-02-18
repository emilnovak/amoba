# Hasznos linkek:
# Algorithms Explained – minimax and alpha-beta pruning: https://youtu.be/l-hh51ncgDI
#   --> Source Code https://pastebin.com/rZg1Mz9G
# 5 in a row implementation of minimax: http://cs.oswego.edu/~yxia/coursework/csc466/project/paper.pdf

import math

def minimax(position, depth,  maximizingPlayer, alpha = -math.inf, beta = math.inf):
    if depth == 0 ''' or game over in position''':
        return ''' static evaluation of position'''

    if maximizingPlayer:
        maxEval = -math.inf
        for child in position:
            eval = minimax(child, depth - 1, false, alpha, beta)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha
                break
        return maxEval
    else:
        minEval = math.inf
        for child in position:
            eval = minimax(child, depth - 1, true, alpha, beta)
            minEval = min(beta, eval)
            if beta <= alpha
                break
        return minEval
