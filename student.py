
import asyncio
import getpass
import json
from models.SearchTree import SearchTree
from models.SearchDomain import SearchDomain
from models.SearchProblem import SearchProblem
from models.Walker import Walker
import os
import websockets
from mapa import Map
from multiprocessing import Process, Queue
import time

from models.AStar import astar_get_path
from consts import Tiles
from mapa import Map
from models.Utils import can_push_box, get_adjs_pos, switch_tiles

queue = Queue()

def bot(level):
    mapa = Map(f"./levels/{level}.xsb")
    rules = SearchDomain()
    rules.read_deadlocks(mapa)
    problem = SearchProblem(rules, mapa)
    solver = SearchTree(problem)
    answer = solver.search()
    queue.put(answer)

def check_timeout_reached(state, timeout, process):
    if state['step'] >= timeout:
        print("O algoritmo nao conseguiu completar o nivel {0} a tempo".format(state['level']))
        exit(0)

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)
        timeout = game_properties["timeout"]

        game_loaded = False
        walker = Walker()
        start_time = time.time()
        process = None

        while True:
            state = json.loads(await websocket.recv())
            if not game_loaded:
                game_loaded = True
                print("level: {0}".format(state['level']))
                process = Process(target=bot, args=(state['level'],))
                start_time = time.time()
                process.daemon = True
                process.start()
            else: check_timeout_reached(state, timeout, process)
            try:
                if not queue.empty():
                    game_loaded = False
                    level = state['level']
                    walker.add_solution(queue.get())
                    if not walker.has_moves():
                        print("O algoritmo nao conseguiu completar o nivel {0}".format(level))
                        exit(0)
                    
                    print("nivel {0} terminado em {1} segundos".format(level, round(time.time()-start_time, 3)))
                    while walker.has_next_move():
                        state = json.loads(await websocket.recv())
                        check_timeout_reached(state, timeout, process)
                        key = walker.next_move(state)
                        if key == "ERROR":
                            print("Erro com o mapa de nivel {0}".format(level))
                            exit(0)
                        await websocket.send(json.dumps({"cmd": "key", "key": key}))
                    walker.clean()
                else:
                    await websocket.send(json.dumps({"cmd": "key", "key": ""}))
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))