import json
import parameters
import os

def Init_record_file(file_name, initial_string):
    if not os.path.exists(parameters.record_files_folder):
            os.makedirs(parameters.record_files_folder)
    with open(file_name.format(file_path = parameters.record_files_folder, idx = parameters.idx), 'w', encoding="utf-8") as file:
        file.write(initial_string)

def Record_txt(file_name, input_string):
    with open(file_name.format(file_path = parameters.record_files_folder, idx = parameters.idx), 'a', encoding="utf-8") as file:
        file.write(input_string)

def Record_json(file_name, input_dict):
    with open(file_name.format(file_path = parameters.record_files_folder, idx = parameters.idx), 'a', encoding="utf-8") as file:
        json.dump(input_dict, file, indent = 4)
