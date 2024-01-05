import json
import parameters

idx = 0

with open(parameters.data_path_crosswords, 'r') as file:
    answer = json.load(file)

with open(parameters.json_file_name.format(idx = idx), 'r') as file:
    crosswords = json.load(file)

crosswords = crosswords['answer']
print(crosswords)
answer = [x.lower() for x in answer[0][1]]
print(answer)

for i in range(5):
    if answer[i * 5 : (i + 1) * 5] == crosswords[i * 5 : (i + 1) * 5]:
        print('correct')
    else:
        print('wrong')
    print(crosswords[i * 5 : (i + 1) * 5])
    print(answer[i * 5 : (i + 1) * 5])
for i in range(5):
    if answer[i::5] == crosswords[i::5]:
        print('correct')
    else:
        print('wrong')
    print(crosswords[i::5])
    print(answer[i::5])