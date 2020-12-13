import getpass
import asyncio
import json
from models.SearchTree import SearchTree
from models.SearchDomain import SearchDomain
from models.SearchProblem import SearchProblem
from models.Walker import Walker
from mapa import Map

import os
import websockets
from multiprocessing import Process, Queue
import time
from mapa import Map

queue = Queue()

def bot(level):
    mapa = Map(f"./levels/{level}.xsb")
    rules = SearchDomain()
    problem = SearchProblem(rules, mapa)
    solver = SearchTree(problem)
    answer = solver.search()
    queue.put(answer)

def check_timeout_reached(state, timeout):
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
        T = 1/game_properties['fps']

        game_loaded = False
        walker = Walker()
        start_time = time.time()
        process = None
        divisions = 10

        while True:
            state = json.loads(await websocket.recv())
            if not game_loaded:
                game_loaded = True
                print("level: {0}".format(state['level']))
                process = Process(target=bot, args=(state['level'],))
                start_time = time.time()
                process.daemon = True
                process.start()
            else: check_timeout_reached(state, timeout)
            try:
                sleep_time = T/divisions
                for _ in range(divisions):
                    time.sleep(sleep_time)
                    if not queue.empty():
                        game_loaded = False
                        level = state['level']
                        walker.add_solution(queue.get())
                        if not walker.has_next_move():
                            print("O algoritmo nao conseguiu completar o nivel {0}".format(level))
                            exit(0)
                        
                        print("nivel {0} terminado em {1} segundos com {2} passos".format(level, round(time.time()-start_time, 3), len(walker.moves)))
                        while walker.has_next_move():
                            state = json.loads(await websocket.recv())
                            check_timeout_reached(state, timeout)
                            key = walker.next_move(state)
                            if key == "ERROR":
                                print("Erro com o mapa de nivel {0}".format(level))
                                exit(0)
                            await websocket.send(json.dumps({"cmd": "key", "key": key}))
                            time.sleep(sleep_time)
                        walker.clean()
                        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
                        msg = await websocket.recv()
                        game_properties = json.loads(msg)
                        timeout = game_properties["timeout"]
                        T = 1/game_properties['fps']
                        break
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
