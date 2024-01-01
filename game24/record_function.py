import json
import parameters

def Init_record_file(file_name, initial_string):
    with open(file_name.format(idx = parameters.idx), 'w') as file:
        file.write(initial_string)

def Record_txt(file_name, input_string):
    with open(file_name.format(idx = parameters.idx), 'a') as file:
        file.write(input_string)

def Record_json(file_name, input_dict):
    with open(file_name.format(idx = parameters.idx), 'a') as file:
        json.dump(input_dict, file, indent = 4)
