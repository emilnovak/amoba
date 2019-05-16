'''
@author: Jozsef, Steger
@date: 9. May 2019
@summary: a basic API for the gomuku game. Handles users and tables.
'''
import pwgen
import logging
import time

import amoba

logger = logging.getLogger('gomuku.api')
players = {}
tables_2_join = {}
tID_next = 1
tables = {}
t0 = {}
t_cum = {}

class AuthError(Exception):
    pass

def lost_socket(sock):
    found = False
    for nick, (_, s) in players.items():
        if s == sock:
            found = True
            break
    if not found:
        logger.error("No player record found for socket {}".format(sock))
        return
    del players[nick]
    logger.info("Deregistered {} - {} players left".format(nick, len(players)))
    if nick in tables_2_join:
        del tables_2_join[nick]
        logger.info("Removed from waiting list {}".format(nick))
        return
    opponent = None
    for table_id, (A, B, _) in tables.items():
        if A == nick:
            opponent = B
            break
        elif B == nick:
            opponent = A
            break
    if opponent:
        del tables[table_id]
        sock_opponent = players[opponent][1]
        del players[opponent]
        logger.info("Deregistered {} - {} players left".format(opponent, len(players)))
        logger.warning("{0} was playing with {1}. Notifying {1} to exit".format(nick, opponent))
        return { 'method': 'exit', 'recipient': sock_opponent, 'reason': "{} disconnected from the game".format(nick) }

def register_player(nick, sock = None):
    assert not nick in players, "Already registered"
    p = pwgen.pwgen(16)
    players[nick] = (p, sock)
    logger.info('New player {} - {} players registered so far'.format(nick, len(players)))
    logger.warning(players) #debug
    return { 'secret': p, 'recipient': sock }

def auth(nick, secret, sock):
    assert nick in players, "Not registered"
    p, s = players[nick]
    if p != secret:
        raise AutError("Wrong password provided by {}".format(nick))
    if s != sock:
        raise AuthError("Socket missmatch {} {} =/= {}".format(nick, s, sock))

def new_play(nick, secret, sock = None):
    auth(nick, secret, sock)
    assert not nick in tables_2_join, "Unjoined table left"
    tables_2_join[nick] = amoba.Table()
    logger.info('{} is waiting for an opponent'.format(nick))
    return { }

def joinable_plays(nick, secret, sock = None):
    auth(nick, secret, sock)
    plays = [ n for n in tables_2_join.keys() ]
    if nick in plays:
        plays.remove(nick)
    logger.debug('{} lists who are waiting to play: {}'.format(nick, plays))
    return { 'waiting_players': plays, 'recipient': sock }

def join_play(nick, secret, sock = None, nick_opponent = None):
    global tID_next
    auth(nick, secret, sock)
    assert nick_opponent in tables_2_join, "Table not found"
    assert nick_opponent != nick, "Cannot play with yoursef"
    t = tables_2_join.pop(nick_opponent)
    tID = tID_next
    tID_next += 1
    tables[tID] = (nick_opponent, nick, t)
    logger.info('{0} and {1} are going to play. Creator moves first: {0}'.format(nick_opponent, nick))
    t0[nick_opponent] = time.time()
    t_cum[nick] = 0
    t_cum[nick_opponent] = 0
    return [ { 'table_id': tID  }, { 'method': 'move', 'recipient': players[nick_opponent][1], 'last_move': (None, None), 'opponent': nick, 'table_id': tID } ]

def move(nick, secret, sock = None, table_id = None, move = (None, None)):
    auth(nick, secret, sock)
    assert table_id in tables, "Table not found any more"
    pA, pB, t = tables[table_id]
    assert nick in [ pA, pB ], "This table is not played by you"
    if nick == pA:
        p = t.player_A
        nick_opponent = pB
    else:
        p = t.player_B
        nick_opponent = pA
    x, y = move
    sock_opponent = players[nick_opponent][1]
    if t.move(p, x, y) is None:
        w = pA if t._winner == t.player_A else pB if t._winner == t.player_B else None
        t1 = time.time()
        t_cum[nick] += t1 - t0[nick]
        del t0[pA]
        del t0[pB]
        del tables[table_id]
        del players[pA]
        del players[pB]
        logger.info("Deregistered {} and {} - {} players left".format(pA, pB, len(players)))
        logger.info('The play between {} (used {} seconds) and {} (used {} seconds) is over. The winner is {} (was it a draw? {})'.format(pA, t_cum.pop(pA), pB, t_cum.pop(pB), w, t._draw))
        return [ { 'method': 'exit', 'recipient': sock_opponent, 'draw': t._draw, 'winner': w, 'table': t }, { 'method': 'exit', 'draw': t._draw, 'winner': w, 'table': t } ]
    else:
        t1 = time.time()
        t_cum[nick] += t1 - t0[nick]
        t0[nick_opponent] = t1
        logger.debug('{} moved consumed {} seconds thinking'.format(nick, t_cum[nick]))
        return { 'method': 'move', 'recipient': sock_opponent, 'last_move': move, 'opponent': nick, 'table_id': table_id, 'table': t }

def show_table(nick, secret, sock = None, table_id = None):
    auth(nick, secret, sock)
    assert table_id in tables, "Table not found any more"
    pA, pB, t = tables[table_id]
    assert nick in [ pA, pB ], "This table is not played by you"
    logger.debug('{} asks the table'.format(nick))
    return { 'table': t }

f_lut = dict([ (f.__name__, f) for f in [ register_player, auth, new_play, joinable_plays, join_play, move, show_table ] ])

if __name__ == '__main__':
    import sys

    A, B = 'krumpli', 'brokkoli'

    secretA = register_player(A)['secret']
    print ('secret', secretA)
    secretB = register_player(B)['secret']
    print ('secret', secretB)
    try:
        register_player(A)
        print ("ERROR: double registration")
        sys.exit(1)
    except AssertionError as e:
        print ("OK: cannot double register:", e)

    try:
        new_play(A, secretA[::-1])
        print ("ERROR: password not checked properly")
    except AssertionError as e:
        print ("OK: password is checked:", e)
    empty = new_play(A, secretA)
    print ("new play, empty", empty)
    try:
        new_play(A, secretA)
        print ("ERROR: double table allocation")
        sys.exit(1)
    except AssertionError as e:
        print ("OK: cannot create table twice:", e)

    jpr = joinable_plays(A, secretA)
    print ("Joinable plays response to A", jpr)
    jpr = joinable_plays(B, secretB)
    print ("Joinable plays response to B", jpr)

    npr = join_play(B, secretB, nick_opponent = 'krumpli')
    print("Joined play responses", npr)
    plid = npr[0]['table_id']
    print ("table_id", plid)

    mr = move(A, secretA, None, plid, (5, 5))
    print ("Move response", mr)

    print (show_table(A, secretA, None, plid)['table'])
