import json
import parameters
import record_function as record

def acc(crosswords, idx):
    acc_dict = {'letter': 0, 'word': 0, 'game': 0}
    with open(parameters.data_path_crosswords, 'r') as file:
        answer = json.load(file)
    
    answer = [x.lower() for x in answer[idx][1]]
    crosswords = [x.lower() for x in crosswords]
    print(crosswords)
    print(answer)

    for i in range(len(answer)):
        if crosswords[i] == answer[i]:
            acc_dict['letter'] += 1
    
    for i in range(5):
        correct = True
        for j in range(5):
            if answer[j + (i * 5)] == crosswords[j + (i * 5)]:
                print(f'{answer[j + (i * 5)]}, {crosswords[j + (i * 5)]}  correct')
            else:
                print(f'{answer[j + (i * 5)]}, {crosswords[j + (i * 5)]}  wrong')
                correct = False
                break
        if correct == True:
            acc_dict['word'] += 1
            print(crosswords[i * 5 : (i + 1) * 5])
            print(answer[i * 5 : (i + 1) * 5])

    for i in range(5):
        correct = True
        for j in range(5):
            if answer[i + (j * 5)] == crosswords[i + (j * 5)]:
                print(f'{answer[i + (j * 5)]}, {crosswords[i + (j * 5)]}  correct')
            else:
                print(f'{answer[i + (j * 5)]}, {crosswords[i + (j * 5)]}  wrong')
                correct = False
                break
        if  correct == True:
            acc_dict['word'] += 1
            print(crosswords[i::5])
            print(answer[i::5])
            
    if acc_dict['word'] == 10:
        acc_dict['game'] += 1

    record.Record_txt(parameters.acc_file_name, 'idx ' + str(idx) + ': '  + ', ' + str(acc_dict) + '\n' + str(crosswords) + '\n' + str(answer) + '\n')
    return acc_dict
