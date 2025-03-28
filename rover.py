import numpy as np
import random
import hashlib
import string

# Function to handle path processing for each rover
def process_rover_path(rover, minefield, mines):
    rover[2] = 'Moving'
    filename = f'path_{rover[0]}.txt'
    if not rover[1]: return rover, mines
    cmnd_strng = rover[1].upper()               
    current_row, current_column = rover[3]                                  
    current_direction = rover[5]
    num_row = len(minefield)
    num_column = len(minefield[0])                               
    path = np.zeros((num_row, num_column), dtype=int)   
    path[current_row][current_column] = 1                                      
    explode = False                                              
    for cmnd in cmnd_strng:
        rover[4] += cmnd
        if cmnd == 'M':
            print(f'M: {current_row}.{current_column}',end='')
            if minefield[current_row][current_column] == 1:
                explode = True
            else:
                if current_direction == 0:
                    if current_row - 1 > -1: current_row -= 1
                elif current_direction == 1:
                    if current_column + 1 < num_column: current_column += 1
                elif current_direction == 2:
                    if current_row + 1 < num_row: current_row += 1
                elif current_direction == 3:
                    if current_column - 1 > -1: current_column -= 1
            path[current_row][current_column] = 1
            print(f' to {current_row}.{current_column}')
        elif cmnd == 'R':
            print(f'R: {current_direction}',end='')
            current_direction = (current_direction + 1) % 4
            print(f' to {current_direction}')
        elif cmnd == 'L':
            print(f'L: {current_direction}',end='')
            current_direction = (current_direction - 1) % 4
            print(f' to {current_direction}')
        elif cmnd == 'D':
            print('D')
            if minefield[current_row][current_column] == 1:
                for i, mine in enumerate(mines):
                    serial_number, [row, column], status = mine
                    if row == current_row and column == current_column:
                        disarm_mine(serial_number)
                        mines[i][2] = 'Deactivated'
                minefield[current_row][current_column] = 0
            else:
                minefield[current_row][current_column] = 0
        with open(filename, 'w') as f:
            for i in range(num_row):
                for j in range(num_column):
                    if path[i][j] == 0:
                        c = '0'
                    else:
                        c = '*'
                    f.write(c+" ")
                f.write("\n")
        if explode:
            rover[1] = None
            rover[2] = 'Eliminated'
            rover[3] = [current_row, current_column]
            rover[4] = ''
            rover[5] = 2
            rover[6].append(path.tolist())
            return rover, mines
    rover[1] = None
    rover[2] = 'Finished'
    rover[3] = [current_row, current_column]
    rover[4] = ''
    rover[5] = current_direction
    rover[6].append(path.tolist())
    return rover, mines

# Function disarming mines
def disarm_mine(serial_number):
    print("\nDisarming mine...")
    is_not_valid = True
    characters = string.ascii_letters + string.digits
    while is_not_valid:
        pin = ''.join(random.choice(characters) for c in range(4))
        temporary_mine_key = f"{pin}{serial_number}"
        hashed_key = hashlib.sha256(temporary_mine_key.encode()).hexdigest()
        if hashed_key.startswith("00000"):
            print(f"Found valid pin: {hashed_key}.\n")
            is_not_valid = False
            return hashed_key