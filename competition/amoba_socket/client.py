'''
@author: Jozsef, Steger
@date: 10 May 2019
@summary: the client side socket layer for the gomuku play. It calls back to gomuku implementation
'''
import sys
import socket
import select
import pickle
import queue
import threading
import time
import argparse
import logging

import cb_amoba
import amoba

stop = threading.Event()
msg_in = queue.Queue()
msg_out = queue.Queue()

secret = None
join = None
table_id = None
last_move = None

t = None
iam = None
opponent = None


def do_apply(d):
    global secret
    global join
    global table_id
    global last_move
    global table, iam, opponent
    error = None
    method = None
    if 'error' in d:
        error = d['error']
        logger.error ("Server error {}".format(error))
    if 'secret' in d:
        secret = d.pop('secret')
    if 'waiting_players' in d:
        nicks = d.pop('waiting_players')
        if len(nicks):
            logger.debug ("Players waiting {}".format(nicks))
            join = cb_amoba.select_opponent(nicks)
        else:
            join = -1
    if 'table_id' in d:
        table_id = d.pop('table_id')
    if 'opponent' in d:
        join = d.pop('opponent')
    if 'last_move' in d:
        last_move = d.pop('last_move')
        if last_move != (None, None):
            table.move(opponent, last_move[0], last_move[1])
    if 'method' in d:
        method = d.pop('method')
    if method == 'move' or error in [ 'Out of table', 'This place is already occupied', ]:
        logger.debug ("You move now! (last move of {} was {})".format(join, last_move))
        t0 = time.time()
        next_move = cb_amoba.move(last_move = last_move, table = str(table), history = table.history)
        t = time.time()
        try:
            table.move(iam, next_move[0], next_move[1])
        except:
            pass
        f = { 'method': 'move', 'move': next_move, 'table_id': table_id, 'nick': nick, 'secret': secret }
        msg_out.put(f)
        return
    if method == 'exit':
        if 'winner' in d:
            logger.info ("The winner is {}".format(d['winner']))
            w = 'you' if d['winner'] == nick else d['winner']
            print ("The winner is {}".format(w))
            print (d['table'])
        if 'reason' in d:
            logger.info ("The server notified to exit because {}".format(d['reason']))
            print ("The server notified to exit because {}".format(d['reason']))
        stop.set()
    if error:
        stop.set()

def processor():
    msgbuffer = b''
    logger.info ("processor loop started")
    while not stop.is_set():
        try:
            call = msg_out.get_nowait()
            logger.debug ("-> {}".format(call))
            s.sendall(pickle.dumps(call) + sep)
        except queue.Empty:
            pass
        except BrokenPipeError:
            logger.error('Lost connection to the server')
            print ('Lost connection to the server exiting...')
            stop.set()
            continue
        try:
            resp = msg_in.get_nowait()
            msgbuffer += resp
            while sep in msgbuffer:
                first, msgbuffer = msgbuffer.split(sep, 1)
                extracted = pickle.loads(first)
                logger.debug ("<- {}".format(extracted))
                do_apply(extracted)
        except queue.Empty:
            time.sleep(args.choke)
    logger.info ("processor loop stopped")

def statemachinery():
    global table
    global iam
    global opponent

    f = { 'method': 'register_player', 'nick': nick }
    msg_out.put(f)
    while secret is None and not stop.is_set():
        time.sleep(.1)

    if stop.is_set():
        logger.warning ("returning too early")
        return

    f = { 'method': 'joinable_plays', 'nick': nick, 'secret': secret }
    msg_out.put(f)
    while join is None:
        time.sleep(.1)

    table = amoba.Table()
    if join == -1:
        logger.info ("requesting new table")
        f = { 'method': 'new_play', 'nick': nick, 'secret': secret }
        iam = table.player_A
        opponent = table.player_B
    else:
        logger.info ("joining a game against {}".format(join))
        f = { 'method': 'join_play', 'nick': nick, 'secret': secret, 'nick_opponent': join }
        opponent = table.player_A
        iam = table.player_B
    msg_out.put(f)

    logger.info ("play loop")
    while not stop.is_set():
        time.sleep(.1)
    logger.info ("play loop stopped")

def cleanup():
    stop.set()
    logger.warning ("stop event")
    if smt:
        logger.debug ("joining play loop")
        smt.join()
    if pt:
        logger.debug ("joining processor loop")
        pt.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("nick", help = "nickname to identify you", type = str)
    parser.add_argument("--choke", help = "sleep for some time if nothing to send/receive", type = float, default = 1e-5)
    parser.add_argument("--sep", help = "separator of messages", type = bytes, default = b'vetel')
    parser.add_argument("-s", "--strategy", help = "strategy implementation", type = str, default = 'random')
    parser.add_argument("-p", "--port", help = "server port", type = int, default = 50000)
    parser.add_argument("--ip", help = "server to connect to", type = str, default = 'localhost')
    parser.add_argument("-v", help = "logging verbosity", type = int, default = logging.DEBUG)
    parser.add_argument("-l", "--logfile", help = "logfile", type = str, default = '')
    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(args.v)
    h = logging.FileHandler(args.logfile) if args.logfile else logging.StreamHandler()
    h.setLevel(args.v)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    h.setFormatter(formatter)
    logger.addHandler(h)
    logger = logging.getLogger('gomuku.client')

    sep = args.sep
    nick = args.nick

    cb_amoba.move = cb_amoba.strategies[args.strategy] if args.strategy in cb_amoba.strategies else cb_amoba.strategies['random']
    logger.info ("{} is playing {}".format(nick, args.strategy))

    s = None
    smt = None
    pt = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(.1)
        s.connect((args.ip, args.port))
        logger.info ("socket open")

        smt = threading.Thread(target = statemachinery)
        smt.start()

        pt = threading.Thread(target = processor)
        pt.start()

        choke = False
 
        while not stop.is_set():
            if choke:
                time.sleep(args.choke)
            readable, writable, exceptional = select.select([s], [s], [s])
            if s in readable:
                data = s.recv(1024)
                if data:
                    msg_in.put(data)
                    choke = False
                else:
                    choke = True
            if s in writable:
                choke = True
            if s in exceptional:
                logger.error ('exception in connection', s)
                break

    except KeyboardInterrupt:
        logger.info('Interrupted')
    except Exception as e:
        logger.error(e)
    finally:
        cleanup()
        if s:
            s.close()
            logger.info ("socket closed")
    
    sys.exit(0)

