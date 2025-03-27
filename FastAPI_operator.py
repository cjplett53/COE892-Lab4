import requests

url = 'http://127.0.0.1:8000/'

def get_selection():
    selection = int(input('\nMain Menu\n 1: Map\n 2: Mines\n 3: Rovers\nPlease select command: '))
    if selection < 1 or selection > 3:
        print('Error: please select 1, 2, or 3.')
        get_selection()
    return selection

def get_map_selection():
    selection = int(input('\nMap Menu\n 1: Retrieve map\n 2: Update map\nPlease select command: '))
    if selection < 1 or selection > 2:
        print('Error: please select 1, or 2.')
        get_map_selection()
    return selection

def get_mines_selection():
    selection = int(input('\nMines Menu\n 1: Retrieve list of mines\n 2: Retrieve a single mine\n 3: Delete a mine\n 4: Create a mine\n 5: Update a mine\nPlease select command: '))
    if selection < 1 or selection > 5:
        print('Error: please select 1, 2, 3, 4, or 5.')
        get_map_selection()
    return selection

def get_rovers_selection():
    selection = int(input('\nRovers Menu\n 1: Retrieve list of rovers\n 2: Retrive a single rover\n 3: Create a rover\n 4: Delete a rover\n 5: Send commands to rover\n 6: Dispatch a rover\nPlease select command: '))
    if selection < 1 or selection > 6:
        print('Error: please select 1, 2, 3, 4, 5, or 6.')
        get_rovers_selection()
    return selection

def display_map(map):
    print('\nCurrent Minefield')
    num_columns = len(map)
    num_rows = len(map[0])
    for i in range(num_columns):
        for j in range(num_rows):
            print(f'{map[i][j]} ', end='')
        print()

def display_mines(mines):
    print('Current Mine Listing')
    for id, mine in enumerate(mines):
        print(f'ID: {id}, Serial Number: {mine[0]}, Location: ({mine[1][0]}, {mine[1][1]})')

def display_rovers(rovers):
    if rovers: print('\nRovers')
    else: print('\nThere are no rovers currently.')
    for id, rover in enumerate(rovers):
        print(f'ID: {id}, Path: {rover[1]}, Status: {rover[2]}, Current Location: {rover[3]}')

def commence_operations():
    print('\nWelcome to FastAPI Operations!\n')
    while True:
        selection = get_selection()
        # Maps selections made below
        if selection == 1: 
            map_selection = get_map_selection()
            if map_selection == 1:
                endpoint = f'{url}map'
                response = requests.get(endpoint)
                if response.status_code == 200:
                    map_data = response.json()
                    map = map_data['map']
                    display_map(map)
            elif map_selection == 2:
                endpoint = f'{url}map'
                num_rows = int(input('\nPlease enter the number of rows: '))
                num_columns = int(input('Please enter the number of columns: '))
                payload = {'num_rows': num_rows, 'num_columns': num_columns}
                response = requests.put(endpoint, json=payload)
                if response.status_code == 200:
                    map_data = response.json()
                    map = map_data['map']
                    display_map(map)
                else: print('System error occurred during map update.')
        # Mines selections made below
        elif selection == 2:
            mines_selection = get_mines_selection()
            if mines_selection == 1:
                endpoint = f'{url}mines'
                response = requests.get(endpoint)
                if response.status_code == 200:
                    mines = response.json()
                    display_mines(mines)
            elif mines_selection == 2:
                id = int(input('\nPlease enter ID of mine to retrieve: '))
                endpoint = f'{url}mines/{id}'
                response = requests.get(endpoint)
                if response.status_code == 200:
                    mine_data = response.json()
                    mine = mine_data['mine']
                    if mine: print(f'Mine {mine[0]} found at ({mine[1][0]}, {mine[1][1]}).')
                    else: print(f'No mine found with {serial_number} as serial number.')
            elif mines_selection == 3:
                id = input('\nPlease enter ID of mine to delete: ')
                endpoint = f'{url}mines/{id}'
                response = requests.delete(endpoint)
                if response.status_code == 200:
                    message = response.json()
                    print(message)
            elif mines_selection == 4:
                endpoint = f'{url}mines'
                serial_number = input('\nPlease enter mine serial number: ')
                row = int(input('Please enter row location: '))
                column = int(input('Please enter column location: '))
                payload = {'serial_number': serial_number, 'row': row, 'column': column}
                response = requests.post(endpoint, json=payload)
                if response.status_code == 200:
                    message = response.json()
                    print(message)
                else: print('System error occurred during creation of mine.')
            elif mines_selection == 5:
                id = int(input('\nPlease enter ID of mine you want to update: '))
                serial_number = None
                row = None
                column = None
                choice = input('Would you like to change serial number? (y/n) ')
                if choice == 'y': serial_number = input('Enter serial number: ')
                choice = input('Would you like to change row location? (y/n) ')
                if choice == 'y': row = int(input('Enter row location: '))
                choice = input('Would you like to change column location? (y/n) ')
                if choice == 'y': column = int(input('Enter column location: '))
                endpoint = f'{url}mines/{id}'
                data = {"id": id}
                if serial_number is not None:
                    data["serial_number"] = serial_number
                if row is not None:
                    data["row"] = row
                if column is not None:
                    data["column"] = column
                response = requests.put(endpoint, json=data)
                if response.status_code == 200:
                    message = response.json()
                    print(message)
                else: print('System error occurred during updating of mine.')
        # Rovers selections below
        elif selection == 3:
            rovers_selection = get_rovers_selection()
            if rovers_selection == 1:
                endpoint = f'{url}rovers'
                response = requests.get(endpoint)
                if response.status_code == 200:
                    rovers = response.json()
                    display_rovers(rovers)
                else: print('System error occured during retrieval of list of rovers.')
            elif rovers_selection == 2:
                id = int(input('\nPlease enter ID of rover you wish to retrieve: '))
                endpoint = f'{url}rovers/{id}'
                response = requests.get(endpoint)
                if response.status_code == 200:
                    rover_data = response.json()
                    rover = rover_data['rover']
                    if rover: print(f'Rover {rover[0]} is {rover[2]} and has path {rover[1]}.')
                    else: print(f'No rover found with {id} as ID.')
                else: print('System error occurred during retrieval of rover.')
            elif rovers_selection == 3:
                path = input('\nPlease enter string of commands: ')
                endpoint = f'{url}rovers'
                payload = {'path': path}
                response = requests.post(endpoint, json=payload)
                if response.status_code == 200:
                    message = response.json()
                    print(message)
                else: print('System error occurred during creation of rover.')
            elif rovers_selection == 4:
                id = int(input('\nPlease enter ID of rover you wish to delete: '))
                endpoint = f'{url}rovers/{id}'
                response = requests.delete(endpoint)
                if response.status_code == 200:
                    message = response.json()
                    print(message)
                else: print('System error occurred during deletion of rover.')
            elif rovers_selection == 5:
                id = int(input('\nPlease enter ID of rover you wish to send commands to: '))
                new_path = input('Please enter updated commands to send to Rover: ')
                endpoint = f'{url}rovers/{id}'
                payload = {'new_path': new_path}
                response = requests.put(endpoint, json=payload)
                if response.status_code == 200:
                    message = response.json()
                    print(message)
                else: print('System error occurred during sending of rover commands.')
            elif rovers_selection == 6:
                id = int(input('\nPlease enter ID of rover you wish to dispatch: '))
                endpoint = f'{url}rovers/{id}/dispatch'
                response = requests.post(endpoint)
                if response.status_code == 200:
                    rover = response.json()
                    if rover[2] == 'Finished':
                        print(f'Rover {rover[0]} has successfully completed commands and is awaiting further orders at {rover[3]}.')
                    else:
                        print(f'Rover {rover[0]} has been eliminated.')
                else: print('System error occurred during deletion of rover.')

if __name__ == '__main__':
    commence_operations()