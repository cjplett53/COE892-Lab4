import numpy as np
import random
import hashlib
import string

# Function to handle path processing for each rover
def process_rover_path(rover, minefield, mines):
    filename = f'path_{rover[0]}.txt'
    cmnd_strng = rover[1].upper()               
    current_row = rover[3][0]                                     
    current_column = rover[3][1]                                  
    current_direction = 2
    num_row = len(minefield)
    num_column = len(minefield[0])                               
    path = np.zeros((num_row, num_column), dtype=int)   
    path[current_row][current_column] = 1                                      
    explode = False                                              
    for cmnd in cmnd_strng:
        rover[4] += cmnd
        if cmnd == 'M':
            if minefield[current_row][current_column] == 1:
                explode = True
            else:
                if current_direction == 0:
                    current_row = (current_row - 1) % num_row
                elif current_direction == 1:
                    current_column = (current_column + 1) % num_column
                elif current_direction == 2:
                    current_row = (current_row + 1) % num_row
                elif current_direction == 3:
                    current_column = (current_column - 1) % num_column
            path[current_row][current_column] = 1
        elif cmnd == 'R':
            current_direction = (current_direction + 1) % 4
        elif cmnd == 'L':
            current_direction = (current_direction - 1) % 4
        elif cmnd == 'D':
            if minefield[current_row][current_column] == 1:
                for mine in mines:
                    serial_number, [row, column] = mine
                    if row == current_row and column == current_column:
                        disarm_mine(serial_number)
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
            return rover
    rover[1] = None
    rover[2] = 'Finished'
    rover[3] = [current_row, current_column]
    return rover

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