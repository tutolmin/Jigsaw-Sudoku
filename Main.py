import numpy as np
#from datetime import datetime
#import time

with open('Sudoku_Regions_13.txt') as f:
    content = f.read()
dict_construct = 'regions_dict = {' + content + '}'
regions_dict = {}
exec(dict_construct)
numbers_set = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}


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
    empty_index = find_empty(sudoku_array)
    if not empty_index:
        return True
    available_numbers = find_available_numbers(sudoku_array, empty_index[0], empty_index[1])
    if len(available_numbers) == 0:
        return False
    for x in available_numbers:
        sudoku_array[empty_index] = x
        if solve(sudoku_array):
            return True
        sudoku_array[empty_index] = 0
    # Получаем текущее время
#    now = datetime.now()
#    if now.second == 0:
#        print(sudoku_array)
    return False


sudoku = construct_sudoku_array()

print(find_empty(sudoku))
solve(sudoku)
print(sudoku)
