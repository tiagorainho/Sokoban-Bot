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

import time
import math

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)

        # You can create your own map representation or use the game representation:
        #mapa = Map(game_properties["map"])

        walker = Walker()
        level = 155

        while True:
            error = False
            print("level: {0}".format(level))
            mapa = Map(f"./levels/{level}.xsb")
            rules = SearchDomain()
            rules.read_deadlocks(mapa)
            problem = SearchProblem(rules, mapa)
            solver = SearchTree(problem)
            answer = solver.search()
            walker.add_solution(answer)
            #toc = math.floor(time.process_time()*10)-1
            if not solver.found_solutions():
                print("O algoritmo nao conseguiu")
                exit(0)
            try:
                print("nivel {0} terminado com {1} passos".format(level, len(answer)-1))
                state = json.loads(await websocket.recv())
                #while state["step"] < toc:
                #    await websocket.send(json.dumps({"cmd": "key", "key": ""}))
                #    state = json.loads(await websocket.recv())
                while walker.has_next_move():
                    key = walker.next_move(state)
                    if key == "ERROR":
                        error = True
                        print("Erro com o mapa de nivel {0}, a recomeçar...".format(level))
                        #tratar aqui do erro
                        break
                    await websocket.send(json.dumps({"cmd": "key", "key": key}))
                    state = json.loads(await websocket.recv())
                walker.clean()
                print(solver.num_nodes)
                if not error:
                    level += 1
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