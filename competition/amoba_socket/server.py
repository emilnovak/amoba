'''
@author: Jozsef, Steger
@date: 9. May 2019
@summary: socket server for the gomuku game. peer-to-peer communication is implemented messages travel ar pickled dicts terminated by a constant bytestring
'''
import sys
import socket
import select
import random
import pickle
import queue
import threading
import time
import argparse
import logging

import s_api

stop = threading.Event()
msg_in = queue.Queue()
msg_out = {}
t_heartbeat = {}

def do_apply(s, m):
    todo = pickle.loads(m)
    logger.debug (todo)
    try:
        assert isinstance(todo, dict), "Protocol violation send a dict"
        assert 'method' in todo, "Protocol violation, KeyError method"
        f = s_api.f_lut[todo.pop('method')]
        todo['sock'] = s
        resp = f(**todo)
    except s_api.AuthError as e:
        logger.warning(e)
        resp = { 'error': str(e) }
    except AssertionError as a:
        resp = { 'error': str(a) }
    except Exception as a:
        logger.error("EXCEPTION {}".format(a))
        resp = { 'error': str(a) }
    logger.debug ("resp {}".format(resp))
    return resp

def processor():
    msgbuffer = {}
    logger.info ("processor loop started")
    while not stop.is_set():
        try:
            s, m = msg_in.get_nowait()
            if not s in msgbuffer:
                msgbuffer[s] = b''
            msg = msgbuffer[s] + data
            while sep in msg:
                first, msg = msg.split(sep, 1)
                resp = do_apply(s, first)
                if isinstance(resp, dict):
                    if 'recipient' in resp:
                        to = resp.pop('recipient')
                    else:
                        to = s
                    msg_out[to].put(resp)
                elif isinstance(resp, list):
                    for r in resp:
                        if isinstance(r, dict):
                            if 'recipient' in r:
                                to = r.pop('recipient')
                            else:
                                to = s
                            msg_out[to].put(r)
                        else:
                            logger.error ("API error {} {}".format(s, r))
                else:
                    logger.error ("API error {} {}".format(s, resp))
            msgbuffer[s] = msg
        except queue.Empty:
            time.sleep(args.choke)
    logger.info ("processor loop exited")

def cleanup():
    stop.set()
    logger.info ("stop event")
    if pt:
        logger.info ("joining processor loop")
        pt.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--sep", help = "separator of messages", type = bytes, default = b'vetel')
    parser.add_argument("--choke", help = "sleep for some time if nothing to send/receive", type = float, default = 1e-5)
    parser.add_argument("-p", "--port", help = "server port", type = int, default = 50000)
    parser.add_argument("--ip", help = "interface to use", type = str, default = 'localhost')
    parser.add_argument("-v", help = "logging verbosity", type = int, default = logging.DEBUG)
    parser.add_argument("-l", "--logfile", help = "logfile", type = str, default = '')
    parser.add_argument("-w", "--waitforping", help = "Wait at most this long to receive a message from clients", type = int, default = 30)
    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(args.v)
    h = logging.FileHandler(args.logfile) if args.logfile else logging.StreamHandler()
    h.setLevel(args.v)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    h.setFormatter(formatter)
    logger.addHandler(h)
    logger = logging.getLogger('gomuku.server')

    sep = args.sep
    server = None
    pt = None
    inputs = []
    try:
        pt = threading.Thread(target = processor)
        pt.start()

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        server.bind((args.ip, args.port))
        server.listen(5)
        logger.info ("waiting for connections")

        inputs = [server]
        outputs = []
        choke = False

        while inputs:
            if choke:
                time.sleep(args.choke)
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            t = time.time()
            for s in readable:
                if s is server:
                    connection, client_address = s.accept()
                    logger.info ('new connection from {}'.format(client_address))
                    connection.setblocking(0)
                    inputs.append(connection)
                    msg_out[connection] = queue.Queue()
                    t_heartbeat[connection] = t
                    outputs.append(connection)
                else:
                    try:
                        data = s.recv(1024)
                    except ConnectionResetError:
                        logger.error("Connection reset error {}".format(s))
                        data = None
                    if data:
                        msg_in.put((s, data))
                        t_heartbeat[s] = t
                        choke = False
                    else:
                        choke = True
                        if t - t_heartbeat[s] > args.waitforping:
                            logger.warning ('waited for too long for a heartbeat ping {}'.format(s))
                            if s in outputs:
                                outputs.remove(s)
                            inputs.remove(s)
                            del msg_out[s]
                            del t_heartbeat[s]
                            notify = s_api.lost_socket(s)
                            if notify is not None:
                                logger.info("notification of the other peer")
                                to = notify.pop('recipient')
                                msg_out[to].put(notify)
            for s in writable:
                if not s in msg_out:
                    continue
                try:
                    msg = msg_out[s].get_nowait()
                    s.sendall(pickle.dumps(msg) + sep)
                    t_heartbeat[s] = t
                except queue.Empty:
                    choke = True
            for s in exceptional:
                logger.error ('exception in connection {}'.format(s))
                if s is server:
                    raise Exception("server socket error")
                #################################DUPLICATE
#                if s in outputs:
#                    outputs.remove(s)
#                inputs.remove(s)
#                del msg_out[s]
#                del t_heartbeat[s]
                ##########################################

    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        logger.error (e)
        cleanup()
    finally:
        for s in inputs:
            try:
                sn = s.getsockname() if s is server else s.getpeername()
            except OSError as e:
                sn = s, e
            s.close()
            if s is server:
                logger.info ("server socket closed {}".format(sn))
            else:
                logger.info ("client socket closed {}".format(sn))

    sys.exit(0)
