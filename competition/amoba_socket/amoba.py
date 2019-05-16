'''
@author: Jozsef, Steger
@date: 9. May 2019
@summary: implements an NxN gomuku table for two players.
'''
import numpy
import scipy.signal
import logging

logger = logging.getLogger('gomuku.table')

class Table:
    player_A, player_B = [0, 1]

    def __init__(self, N = 15, n = 5):
        self._history = []
        self._size = N
        self._N2 = N * N
        self._l = n
        self._next = self.player_A
        self._winner = None
        self._draw = False
        self._A = numpy.zeros((N, N))
        self._B = numpy.zeros((N, N))
        self._k = [ numpy.ones((n, 1)), numpy.ones((1, n)), numpy.eye(n), numpy.rot90(numpy.eye(3)) ]
        logger.info('Initialized a new table of {}, to win {} ticks are needed in a line'.format(N, n))

    def __str__(self):
        return str(1 * self._A + 2 * self._B)

    def lastmove(self):
        pl = self.player_A if len(self._history) % 2 else self.player_B
        p = self._history[-1]
        return pl, p % self._size, p // self._size

    @property
    def history(self):
        for i, p in enumerate(self._history):
            P = self.player_B if i % 2 else self.player_A
            yield P, p % self._size, p // self._size

    def move(self, player, x, y):
        assert self._winner is None, "Winner found"
        assert not self._draw, "Table full"
        assert (x >= 0) and (y >= 0) and (x < self._size) and (y < self._size), "Out of table"
        assert player == self._next, "Wait for the other player to move" 
        p = y * self._size + x
        assert not p in self._history, "This place is already occupied"
        self._history.append( p )
        if len(self._history) == self._N2:
            self._draw = True
            logger.info('Draw')
        if player == self.player_A:
            self._A[y, x] = 1
            if self._check(self._A):
                self._winner = self.player_A
                self._next = None
                logger.info('First player wins')
            else:
                self._next = self.player_B
        else:
            self._B[y, x] = 1
            if self._check(self._B):
                self._winner = self.player_B
                self._next = None
                logger.info('Second player wins')
            else:
                self._next = self.player_A
        return self._next if not self._draw else None

    def _check(self, t):
        for k in self._k:
            if scipy.signal.convolve2d(t, k).max() == self._l:
                return True
        return False


if __name__ == '__main__':
    t = Table()
    t.move(t.player_A, 3, 1)
    t.move(t.player_B, 3, 2)
    t.move(t.player_A, 4, 1)
    t.move(t.player_B, 4, 2)
    t.move(t.player_A, 2, 1)
    t.move(t.player_B, 2, 2)
    t.move(t.player_A, 1, 1)
    t.move(t.player_B, 1, 2)
    t.move(t.player_A, 0, 1)
    print(t)
    print (t.lastmove())
    try:
        t.move(t.player_B, 0, 2)
        print (t._winner)
    except AssertionError as e:
        print ("OK", e)



