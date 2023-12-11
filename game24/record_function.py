def Init_record_file(file_name, initial_string):
    with open(file_name, 'w') as file:
        file.write(initial_string)

def Record_txt(file_name, input_string):
    with open(file_name, 'a') as file:
        file.write(input_string)