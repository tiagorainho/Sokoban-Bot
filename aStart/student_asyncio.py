
import asyncio
import getpass
import json
import os
import random
from copy import deepcopy
from consts import *
import time
import sys
import asyncio
import getpass
import json
import os
import websockets
import requests
import re
from models.SearchTree import SearchTree
from models.SearchDomain import SearchDomain
from models.SearchProblem import SearchProblem
from models.Walker import Walker
from mapa import Map

async def solver(puzzle, solution):
    totalTime = 0
    while True:
        tick = time.time()
        game_properties = await puzzle.get()

        mapa = Map(game_properties["map"])
        rules = SearchDomain()
        problem = SearchProblem(rules, mapa)
        solver = SearchTree(problem)
        answer = solver.search()
        walker = Walker()
        walker.add_solution(answer)
        keys = walker.moves
        
        await solution.put(keys)
        totalTime += time.time() - tick
        
async def agent_loop(puzzle, solution, server_address="localhost:8000", agent_name="ez"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        while True:
            try:
                update = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if "map" in update:
                    # we got a new level
                    game_properties = update
                    keys = ""
                    await puzzle.put(game_properties)

                if not solution.empty():
                    keys = await solution.get()

                key = ""
                if len(keys):  # we got a solution!
                    key = keys[0]
                    keys = keys[1:]

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                sys.exit(0)
                return

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = "92996_93134_93002_"

puzzle = asyncio.Queue(loop=loop)
solution = asyncio.Queue(loop=loop)

net_task = loop.create_task(agent_loop(puzzle, solution, f"{SERVER}:{PORT}", NAME))
solver_task = loop.create_task(solver(puzzle, solution))

loop.run_until_complete(asyncio.gather(net_task, solver_task))
loop.close()