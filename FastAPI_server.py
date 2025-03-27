from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import uvicorn
from rover import process_rover_path
from typing import Optional

app = FastAPI(title='Ground Control Server')

def initialize(num_rows=10, num_columns=10):
    # Initially there is no mines and the minefield is 10 by 10
    global minefield
    global mines
    global rovers
    minefield = np.zeros((num_rows, num_columns), dtype=int)
    mines = []
    rovers = []

"""
MAPS
"""

def load_map():
    global minefield
    return minefield

def update_map(num_rows, num_columns):
    global minefield
    minefield = load_map()
    new_minefield = np.zeros((num_rows, num_columns), dtype=int)
    for i in range(num_rows):
        for j in range(num_columns):
            if i < len(minefield) and j < len(minefield[0]):
                new_minefield[i][j] = minefield[i][j]
            else:
                new_minefield[i][j] = 0
    minefield = new_minefield
    return minefield

@app.get('/map')
async def get_map():
    map = load_map()
    return {'map': map.tolist()}

class MapUpdateRequest(BaseModel):
    num_rows: int
    num_columns: int

@app.put('/map')
async def put_map(request: MapUpdateRequest):
    num_rows = request.num_rows
    num_columns = request.num_columns
    updated_map = update_map(num_rows, num_columns)
    return {'map': updated_map.tolist()}

"""
MINES
"""

def load_mines():
    global mines
    return mines

def retrieve_mine(id):
    global mines
    if id < len(mines): return mines[id]
    else: return None

def deactivate_mine(id):
    global mines 
    global minefield
    if id < len(mines):
        mine = mines[id]
        minefield[mine[1][0]][mine[1][1]] = 0
        mines.remove(mine)
        return f'Successfully deleted mine {mine[0]} from ({mine[1][0]}, {mine[1][1]}).'
    else:
        return f'Mine with id {id} not found.'

def activate_mine(serial_number, row, column):
    global minefield
    minefield = load_map()
    if minefield[row][column] == 1:
        return 'Error: Mine already present at this cell.'
    minefield[row][column] = 1
    global mines
    mines.append([serial_number, [row, column]])
    return f'Mine {len(mines)-1} added successfully.'

def update_mine(id, serial_number=None, new_row=None, new_column=None):
    global mines 
    global minefield
    if id < len(mines):
        mine = mines[id]
        if serial_number:
            mine[0] = serial_number
        if new_row or new_column:
            minefield[mine[1][0]][mine[1][1]] = 0
            if new_row:
                mine[1][0] = new_row
            if new_column:
                mine[1][1] = new_column
            minefield[mine[1][0]][mine[1][1]] = 1
        mines[id] = mine
        return f'Mine {mine[0]} updated to location ({mine[1][0]}, {mine[1][1]}).'
    else:
        return f'Incorrect mine ID.' 

class CreateMineRequest(BaseModel):
    serial_number: str
    row: int
    column: int

@app.get('/mines')
async def get_mines():
    mines = load_mines()
    return mines

@app.get('/mines/{id}')
async def get_mine(id: int):
    mine = retrieve_mine(id)
    if mine: 
        return {'mine': mine}
    else:
        return {'mine': None}

@app.delete('/mines/{id}')
async def delete_mine(id: int):
    message = deactivate_mine(id)
    return message

@app.post('/mines')
async def post_mines(request: CreateMineRequest):
    serial_number = request.serial_number
    row = request.row
    column = request.column
    response = activate_mine(serial_number, row, column)
    return response

class UpdateMineRequest(BaseModel):
    id: int
    serial_number: Optional[str] = None
    row: Optional[int] = None
    column: Optional[int] = None

@app.put('/mines/{id}')
async def put_mines(request: UpdateMineRequest):
    id = request.id
    serial_number = request.serial_number
    row = request.row
    column = request.column
    response = update_mine(id, serial_number, row, column)
    return response

"""
ROVERS
"""

def load_rovers():
    global rovers
    return rovers

def create_rover(path):
    global rovers
    id = len(rovers)
    rovers.append([id, path, 'Not Started', [0,0], ''])
    return f'Rover {len(rovers)-1} successfully added.'

def retrieve_rover(id):
    global rovers
    if id < len(rovers): return rovers[id]
    else: return None

def deactivate_rover(id):
    global rovers
    if id < len(rovers):
        rovers.remove(rovers[id])
        return f'Successfully removed rover with ID {id}.'
    else: return f'Rover with ID {id} not found.'

def start_rover(id, new_path):
    global rovers
    if id < len(rovers):
        if rovers[id][2] == 'Not Started' or rovers[id][2] == 'Finished':
            rovers[id][1] = new_path
            return f'Commands sent to Rover {id} available for dispatch.'
        else:
            return f'Commands not sent to Rover {id} unavailable for dispatch.'
    else:
        return f'Rover {id} not found.'
    
def dispatch_rover(id):
    global rovers
    global minefield
    global mines
    if id < len(rovers):
        rover = rovers[id]
        rover = process_rover_path(rover, minefield, mines)
        rovers[id] = rover
        return rover
    else:
        return None
    
@app.get('/rovers')
async def get_rovers():
    rovers = load_rovers()
    return rovers

@app.get('/rovers/{id}')
async def get_rover(id: int):
    rover = retrieve_rover(id)
    if rover:
        return {'rover': rover}
    else:
        return {'rover': None}

class CreateRoverRequest(BaseModel):
    path: str

@app.post('/rovers')
async def post_rovers(request: CreateRoverRequest):
    path = request.path
    message = create_rover(path)
    return message

@app.delete('/rovers/{id}')
async def delete_rovers(id: int):
    message = deactivate_rover(id)
    return message

class RoverUpdate(BaseModel):
    new_path: str

@app.put('/rovers/{id}')
async def put_rover(id: int, update: RoverUpdate):
    message = start_rover(id, update.new_path)
    return message

@app.post('/rovers/{id}/dispatch')
async def post_rover(id: int):
    rover = dispatch_rover(id)
    if rover: return rover
    else: return None

if __name__ == '__main__':
    initialize()
    uvicorn.run(app, host='0.0.0.0', port=8000)