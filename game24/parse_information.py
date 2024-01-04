import json
import parameters
import sympy


with open(parameters.all_json_file_name.format(file_path = parameters.record_files_folder), 'r') as file:
    datas = json.load(file)

for data in datas:
    print(data['answer'])
    print(sympy.simplify(data['answer'].replace('\\', '') == 24))

result = [1 if x['correct'] else 0 for x in datas]
print(result)
    