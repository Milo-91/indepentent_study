import json
import parameters

def acc(crosswords, idx):
    acc_dict = {'letter': 0, 'word': 0, 'game': 0}
    with open(parameters.data_path_crosswords, 'r') as file:
        answer = json.load(file)
    
    answer = [x.lower() for x in answer[idx][1]]
    print(crosswords)
    print(answer)
    
    for i in range(5):
        word_count = 0
        for j in range(5):
            if answer[j + (i * 5)] == crosswords[j + (i * 5)]:
                print(f'{answer[j + (i * 5)]}, {crosswords[j + (i * 5)]}  correct')
                word_count += 1
                acc_dict['letter'] += 1
            else:
                print(f'{answer[j + (i * 5)]}, {crosswords[j + (i * 5)]}  wrong')
        if word_count == 5:
            acc_dict['word'] += 1
            print(crosswords[i * 5 : (i + 1) * 5])
            print(answer[i * 5 : (i + 1) * 5])

    for i in range(5):
        word_count = 0
        for j in range(5):
            if answer[i + (j * 5)] == crosswords[i + (j * 5)]:
                print(f'{answer[i + (j * 5)]}, {crosswords[i + (j * 5)]}  correct')
                word_count += 1
                acc_dict['letter'] += 1
        else:
            print(f'{answer[i + (j * 5)]}, {crosswords[i + (j * 5)]}  wrong')
        if word_count == 5:
            acc_dict['word'] += 1
            print(crosswords[i::5])
            print(answer[i::5])
    if acc_dict['word'] == 10:
        acc_dict['game'] += 1

    return acc_dict
