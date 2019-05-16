'''
@summary: gomuku strategies
'''
import random


def select_opponent(nicks):
    ln = len(nicks)
    if ln == 0:
        print ("Noone is waiting, a new table is created")
        return
    elif len(nicks) == 1:
        print ("Currently {} is waiting to play.".format(nicks[0]))
        print ("Enter -1 if you want a new table")
        r = input()
        if r.strip() == '-1':
            return
        return nicks[0]
    else:
        print ("Currently {} players are waiting to play".format(ln))
        for x, n in enumerate(nicks):
            print ("[{}] {}".format(x, n))
        print ("Select the index. Otherwise a new table is created")
        r = input()
        try:
            return nicks[int(r.strip())]
        except:
            return

def random_strategy(**kw):
    return random.randint(0, 14), random.randint(0, 14)

def human_strategy(**kw):
    '''
    @param kw: keyword argument. Supported arguments are:
        * 'last_move': a tuple of 2 integer values pointing to the opponents last x, y step
        * 'table': a str representing the current table. 0 stands for empty places, 1 stand for the starting players' positions, 2 stands for the next players' positions
        * 'history': a genarator of tuples. Each tuple is of 3 integers. The first integer (0, 1) stand for the starting player and the next player; The second integer and third integer stand for the position in the table. Tuples are generated in the temporal order of the play so far.
    '''
    last_move = kw['last_move']
    table = kw['table']
    history = kw['history']
    print (last_move)
    if last_move == (None, None):
        print ("You move first")
    print (table)
    #for x in history:
    #    print (x)
    while True:
        r = input()
        try:
            x, y = r.split(',', 1)
            print ('...')
            return int(x.strip()), int(y.strip())
        except Exception as e:
            print (e)

strategies = { 'random': random_strategy, 'human': human_strategy }
