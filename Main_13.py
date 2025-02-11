import numpy as np
import traceback
import sys

with open('Sudoku_Regions_13.txt') as f:
    content = f.read()
dict_construct = 'regions_dict = {' + content + '}'
regions_dict = {}
exec(dict_construct)
numbers_set = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}

def fancy_board(sudoku, file=False):

    # Коды для фона разных регионов
    background_colors = {
        'region_13' : '\033[48;5;250m', 
        'region_12' : '\033[48;5;245m', 
        'region_11' : '\033[48;5;233m',
        'region_10' : '\033[48;5;244m', 
        'region_9' : '\033[48;5;232m', 
        'region_8' : '\033[48;5;245m', 
        'region_3' : '\033[48;5;233m',
        'region_7' : '\033[48;5;244m', 
        'region_5' : '\033[48;5;235m', 
        'region_6' : '\033[48;5;243m',  
        'region_4' : '\033[48;5;236m',  
        'region_2' : '\033[48;5;241m',
        'region_1' : '\033[48;5;237m'
    }

    if file:
        orig_stdout = sys.stdout
        f = open('out.txt', 'w')
        sys.stdout = f

    for i in range(sudoku.shape[0]):
        for j in range(sudoku.shape[1]):
            region = find_region(i, j)
            symbol = sudoku[i][j]
            if symbol == 0:
                symbol = '.'
            elif symbol == 10:
                symbol = 'A'                
            elif symbol == 11:
                symbol = 'B'
            elif symbol == 12:
                symbol = 'C'
            elif symbol == 13:
                symbol = 'D'
            print(background_colors[region], symbol, "\033[0m", end='')            
        print()
    
    if file:
        sys.stdout = orig_stdout
        f.close()

def construct_sudoku_array():
    with open('Sudoku_13.txt') as f:

        # Читаем все строки из файла
        lines = f.readlines()

        # Обрабатываем каждую строку
        file_content = []
        for line in lines:
            # Удаляем лишние пробелы и символы новой строки, затем разделяем по запятым
            values = line.strip().split(',')

            # Преобразуем каждое значение в целое число и добавляем в список
            file_content.append([int(x) for x in values])

    sudoku_array = np.array(file_content)
    return sudoku_array


def find_empty(x):
    empty_items_list = []
    for index, item in np.ndenumerate(x):
        if item == 0:
            empty_items_list.append(index)
    if len(empty_items_list) != 0:
        empty_items_num_of_available_numbers = []
        for i in empty_items_list:
            a = len(find_available_numbers(x, i[0], i[1]))
            empty_items_num_of_available_numbers.append(a)

        return empty_items_list[empty_items_num_of_available_numbers.index(min(empty_items_num_of_available_numbers))]
    return None


def find_region(i, j):
    for v, d in regions_dict.items():
        if (i, j) in d:
            return v


def find_regional_numbers_set(x, i, j):
    regional_points = regions_dict[find_region(i, j)]
    regional_points_set = set(x[a] for a in regional_points)
    return regional_points_set


def find_available_numbers(x, i, j):
    set_1 = set(x[i, :])
    set_2 = set(x[:, j])
    set_3 = find_regional_numbers_set(x, i, j)
    return numbers_set.difference(set_1.union(set_2.union(set_3)))


def solve(sudoku_array):

    stack_trace = ''.join(traceback.format_stack()[:-1])
    print(stack_trace)

    sudoku_orig = np.copy(sudoku_array)
    if not find_singles(sudoku_array):
        # Return sudoku to initial state
        sudoku_array = np.copy(sudoku_orig)
        return False

    empty_index = find_empty(sudoku_array)
    if not empty_index:
        # No empty cells, solution found
        print("MSG: No empty cells")   
        fancy_board(sudoku_array, True)          
        return True
    available_numbers = find_available_numbers(sudoku_array, empty_index[0], empty_index[1])
    if len(available_numbers) == 0:
        # Return sudoku to initial state
        sudoku_array = np.copy(sudoku_orig)
        print("MSG: No available numbers for", empty_index)   
        fancy_board(sudoku_array)          
        return False
    for x in available_numbers:
        sudoku_array[empty_index] = x
        # Trying 
        print("MSG: Trying", x, "at", empty_index, "of", available_numbers)
        fancy_board(sudoku_array)
        if solve(sudoku_array):
            return True
#        sudoku_array[empty_index] = 0
        sudoku_array = np.copy(sudoku_orig)
        find_singles(sudoku_array)
    # Return sudoku to initial state
    sudoku_array = np.copy(sudoku_orig)   
    print("MSG: All possible numbers failed", empty_index, available_numbers)   
    fancy_board(sudoku_array)  
    return False


def find_singles(board):
    """Функция находит и заполняет синглы в судоку."""
    n = len(board)
    found_single = True
    
    print("Looking for new singles")

    while found_single:
        found_single = False

        candidates = np.zeros(shape=(len(board), len(board)), dtype=set)

        # Проходимся по всем клеткам доски
        for i in range(n):
            for j in range(n):
                if board[i][j] == 0:
                    print("Checking", i, j)
                    possible_values = set(range(1, n+1))
                    # Убираем числа, которые уже есть в строке
                    possible_values -= set(board[i])
                    print("Possible values after string check", possible_values)
                    # Убираем числа, которые уже есть в колонке
                    possible_values -= {board[k][j] for k in range(n)}
                    print("Possible values after column check", possible_values)
                    # Убираем числа, которые уже есть в регионе
#                    region_name = find_region((i, j))
                    cells_in_region = regions_dict[find_region(i, j)]
                    possible_values -= {board[x][y] for x, y in cells_in_region}
                    print("Possible values after region check", possible_values)
                    candidates[i][j] = possible_values
                    # Если не осталось возможных значений, конфликт
                    if len(possible_values) == 0:
                        print("MSG: Conflict at", i, j)
                        return False
                    # Если осталось только одно возможное значение, ставим его в клетку
                    if len(possible_values) == 1:
                        value = possible_values.pop()
                        board[i][j] = value
                        print("MSG: Found single", value, "at", i, j)
                        fancy_board(board)
                        found_single = True

        if found_single:
            continue

#        print("Candidates", candidates)

        # проходимся по каждому региону
        for r in regions_dict: 

            # получаем ячейки региона
            cells_in_region = regions_dict[r]
            print("Cells in region", cells_in_region)

            # массив для подсчёта кандидатов региона
            reg_cand = np.zeros(shape=(len(board)), dtype=int)

            # проходимся по каждой ячейке региона
            for c in cells_in_region:

                # берем кандидатов конкретной ячейки
                cell_cand = candidates[c[0]][c[1]]
                print("Cell", c, "candidates", cell_cand)

                # если у ячейки вообще есть кандидаты
                if cell_cand:

                    # проходимся по всем кандидатам ячейки
                    for cand in cell_cand:

                        # учитываем кандидата в массиве
                        reg_cand[cand-1] += 1
            print(reg_cand)

            # массив для подсчёта кандидатов и уже имеющихся значений региона
            possible_values = set(range(1, n+1))
            possible_values -= {board[x][y] for x, y in cells_in_region}
            print("Possible values after region check", possible_values)
            for key, value in enumerate(reg_cand):
                if value > 0:
                    possible_values -= {key+1}
            print("Possible values after region candidates check", possible_values)

            # Если остались значения, которые некуда ставить, конфликт
            if len(possible_values) > 0:
                print("MSG: Conflict in region for", possible_values)
                return False

            # проходимся по всем учтённым кандидатам региона
            for key, value in enumerate(reg_cand):
#                print(key,value)

                # если кандидат в единственном числе в регионе
                if value == 1:

                    # ищем кандидата в ячейках региона
                    for c in cells_in_region:
                        cell_cand = candidates[c[0]][c[1]]
                        if cell_cand:
                            for cand in cell_cand:

                                # кандидат найден, заполняем ячейку доски
                                if key == cand-1:
                                    board[c[0]][c[1]] = cand
                                    print("MSG: Found hidden region single", cand, "at", c[0], c[1])
                                    fancy_board(board)
                                    found_single = True 
        if found_single:
            continue

        # Проходимся по всем клеткам строки
        for l in range(n):

            print( "Line", l)

            # массив для подсчёта кандидатов строки
            line_cand = np.zeros(shape=(len(board)), dtype=int)

            # проходимся по каждой ячейке строки
            for i in range(n):

                # берем кандидатов конкретной ячейки
                cell_cand = candidates[l][i]
                print("Cell", l, i, "candidates", cell_cand)

                # если у ячейки вообще есть кандидаты
                if cell_cand:

                    # проходимся по всем кандидатам ячейки
                    for cand in cell_cand:

                        # учитываем кандидата в массиве
                        line_cand[cand-1] += 1
            print(line_cand)

            # массив для подсчёта кандидатов и уже имеющихся значений строки
            possible_values = set(range(1, n+1))
            possible_values -= {board[l][i] for i in range(n)}
            print("Possible values after line check", possible_values)
            for key, value in enumerate(line_cand):
                if value > 0:
                    possible_values -= {key+1}
            print("Possible values after line candidates check", possible_values)

            # Если остались значения, которые некуда ставить, конфликт
            if len(possible_values) > 0:
                print("MSG: Conflict in line for", possible_values)
                return False

            # проходимся по всем учтённым кандидатам строки
            for key, value in enumerate(line_cand):
#                print(key,value)

                # если кандидат в единственном числе в строке
                if value == 1:

                    # ищем кандидата в ячейках строки
                    for i in range(n):
                        cell_cand = candidates[l][i]
                        if cell_cand:
                            for cand in cell_cand:

                                # кандидат найден, заполняем ячейку доски
                                if key == cand-1:
                                    board[l][i] = cand
                                    print("MSG: Found hidden line single", cand, "at", l, i)
                                    fancy_board(board)
                                    found_single = True 

        if found_single:
            continue

        # Проходимся по всем клеткам столбца
        for c in range(n):

            print( "Column", c)

            # массив для подсчёта кандидатов столбца
            col_cand = np.zeros(shape=(len(board)), dtype=int)

            # проходимся по каждой ячейке столбца
            for i in range(n):

                # берем кандидатов конкретной ячейки
                cell_cand = candidates[i][c]
                print("Cell", i, c, "candidates", cell_cand)

                # если у ячейки вообще есть кандидаты
                if cell_cand:

                    # проходимся по всем кандидатам ячейки
                    for cand in cell_cand:

                        # учитываем кандидата в массиве
                        col_cand[cand-1] += 1
            print(col_cand)

            # массив для подсчёта кандидатов и уже имеющихся значений столбца
            possible_values = set(range(1, n+1))
            possible_values -= {board[i][c] for i in range(n)}
            print("Possible values after column check", possible_values)
            for key, value in enumerate(col_cand):
                if value > 0:
                    possible_values -= {key+1}
            print("Possible values after column candidates check", possible_values)

            # Если остались значения, которые некуда ставить, конфликт
            if len(possible_values) > 0:
                print("MSG: Conflict in column for", possible_values)
                return False

            # проходимся по всем учтённым кандидатам столбца
            for key, value in enumerate(col_cand):
#                print(key,value)

                # если кандидат в единственном числе в столбце
                if value == 1:

                    # ищем кандидата в ячейках столбца
                    for i in range(n):
                        cell_cand = candidates[i][c]
                        if cell_cand:
                            for cand in cell_cand:

                                # кандидат найден, заполняем ячейку доски
                                if key == cand-1:
                                    board[i][c] = cand
                                    print("MSG: Found hidden column single", cand, "at", i, c)
                                    fancy_board(board)
                                    found_single = True 

    return True

sudoku = construct_sudoku_array()

print(find_empty(sudoku))
fancy_board(sudoku)
#find_singles(sudoku)
solve(sudoku)
fancy_board(sudoku)
