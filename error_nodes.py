import re
import os

def error_check():
    question1 = '11 3 3 5'
    answer1 = '12 - 3 = 9 (left: 9 3 5)'

    left, right = answer1.split('left: ')
    left = left.replace('(', '').strip()
    right = right.replace(')', '').strip()
    # print(left)
    # print(right)
    pattern_left = r'(\d+) [\+\-\*\/] (\d+) = (\d+)'
    right_numbers = re.findall(r'\d+', right)
    right_numbers_set = set(map(int, right_numbers))
    match = re.match(pattern_left, left)
    if match:
        print('match: ' + match.group(1) + '  ' + match.group(2) + '  ' + match.group(3))

    if int(match.group(3)) in right_numbers_set:
        print('yes')
        right_numbers_set.remove(int(match.group(3)))
        # print(right_numbers_set)
        right_numbers_set.add(int(match.group(1)))
        right_numbers_set.add(int(match.group(2)))
        question_numbers = re.findall(r'\d+', question1)
        question_numbers_set = set(map(int, question_numbers))
        if right_numbers_set == question_numbers_set:
            print('yes')
        else:
            print('no, upper and lower error')
    else:
        print('no, left and right error')
    
if __name__ == '__main__':
    folder_name = 'k5b3 dfs+sd'
    file_name = 'record_game24_{idx}.txt'
    path = os.path.join(folder_name, file_name.format(idx = 900))
    # print(path)
    with open(path, 'r', encoding = 'utf-8') as file:
        data = file.read()
        print(type(data))
        # print(data)
        data = list(filter(lambda x: x != '' and x != '\'', data.split(r'\n')))
        for d in data:
            print(d)
