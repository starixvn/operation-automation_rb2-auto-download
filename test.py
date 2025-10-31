# init a two dimensional array with 2 rows and 6 columns
COLUMNS = 6


def init_array():
    array = [[0,1,0,1,0,1],[1,0,1,0,1,0]]
    # array = [[0, 1, 0, 1], [1, 0, 1, 0]]
    return array


def copy_array(array):
    new_array = [[0 for _ in range(COLUMNS)] for _ in range(2)]
    for i in range(2):
        for j in range(COLUMNS):
            new_array[i][j] = array[i][j]
    return new_array


def trim_array(array):
    for i in range(2):
        for j in range(COLUMNS):
            if i == 0 and array[0][j] == 0 and array[1][j] == -1:
                array[i][j] = -1
            if i == 1 and array[1][j] == 0 and array[0][j] == -1:
                array[i][j] = -1
    return array


def refine_index(array):
    index_0 = COLUMNS
    for i in range(COLUMNS):
        if array[0][i] != -1:
            index_0 = i
            break
    index_1 = COLUMNS
    for i in range(COLUMNS):
        if array[1][i] != -1:
            index_1 = i
            break
    if index_1 < index_0:
        return index_1
    return index_0


def count_array(array, index):
    count = 1
    trimmed_array = trim_array(array)
    index = refine_index(trimmed_array)
    if index >= COLUMNS - 1:
        return 1

    if trimmed_array[0][index] == 1:
        copied_array1 = copy_array(trimmed_array)
        copied_array1[0][index] = -1
        count_1 = count_array(copied_array1, index)

        if trimmed_array[1][index] == 0:
            copied_array2 = copy_array(trimmed_array)
            copied_array2[1][index] = -1
            copied_array2[0][index] = -1
            count_2 = count_array(copied_array2, index)
            count_1 += count_2
        if index + 1 < COLUMNS and trimmed_array[0][index + 1] == 0:
            copied_array3 = copy_array(trimmed_array)
            copied_array3[0][index + 1] = -1
            copied_array3[0][index] = -1
            count_3 = count_array(copied_array3, index)
            count_1 += count_3
        if (
            index + 1 < COLUMNS
            and trimmed_array[0][index + 1] == 0
            and trimmed_array[1][index] == 0
        ):
            copied_array4 = copy_array(trimmed_array)
            copied_array4[1][index] = -1
            copied_array4[0][index] = -1
            copied_array4[0][index + 1] = -1
            count_4 = count_array(copied_array4, index + 1)
            count_1 += count_4
        count *= count_1

    if trimmed_array[1][index] == 1:
        copied_array1 = copy_array(trimmed_array)
        copied_array1[1][index] = -1
        count_1 = count_array(copied_array1, index)

        if trimmed_array[0][index] == 0:
            copied_array2 = copy_array(trimmed_array)
            copied_array2[1][index] = -1
            copied_array2[0][index] = -1
            count_2 = count_array(copied_array2, index)
            count_1 += count_2
        if index + 1 < COLUMNS and trimmed_array[1][index + 1] == 0:
            copied_array3 = copy_array(trimmed_array)
            copied_array3[1][index + 1] = -1
            copied_array3[1][index] = -1
            count_3 = count_array(copied_array3, index)
            count_1 += count_3
        if (
            index + 1 < COLUMNS
            and trimmed_array[1][index + 1] == 0
            and trimmed_array[0][index] == 0
        ):
            copied_array4 = copy_array(trimmed_array)
            copied_array4[1][index] = -1
            copied_array4[0][index] = -1
            copied_array4[1][index + 1] = -1
            count_4 = count_array(copied_array4, index + 1)
            count_1 += count_4
        count *= count_1
    return count


array = init_array()
count = count_array(array, 0)
print(count)
