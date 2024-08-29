import json
import os

record_files_folder = 'logs/game24/record'
record_file_name = '{file_path}/record_game24_{idx}.txt'
tree_json_file_name = '{file_path}/tree_game24_{idx}.json'
all_json_file_name = '{file_path}/all_tree_game24.json'
acc_file_name = '{file_path}/acc_info_game24.txt'
debug_file_name = '{file_path}/debug_info_{idx}.txt'
propose_cache_file = '{file_path}/propose_cache_{idx}.txt'

def Init_folder_path(folder_path):
     global record_files_folder
     record_files_folder = os.path.join(folder_path, 'record')
     

def Init_record_file(file_name, initial_string, idx = 0):
    global record_files_folder
    if not os.path.exists(record_files_folder):
            os.makedirs(record_files_folder)
    with open(file_name.format(file_path = record_files_folder, idx = idx), 'w') as file:
        file.write(initial_string)

def Record_txt(file_name, input_string, idx = 0):
    global record_files_folder
    with open(file_name.format(file_path = record_files_folder, idx = idx), 'a') as file:
        file.write(input_string)

def Record_json(file_name, input_dict, idx = 0):
    global record_files_folder
    with open(file_name.format(file_path = record_files_folder, idx = idx), 'a') as file:
        json.dump(input_dict, file, indent = 4)