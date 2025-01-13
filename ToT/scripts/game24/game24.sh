#!/usr/bin/env bash

read -p "repeat times: " times
read -p "how much sets: " set_num
today=$(date +%Y-%m-%d)
start_index=900
end_index=1000
algorithm='whole_tree'

for ((i=0;i<set_num;i++));
do
    read -p "Enter k: " k
    read -p "Enter b: " b
    array_k[i]=$k
    array_b[i]=$b
done

for ((i=1;i<=$times;i+=1));
do
    for ((i=0;i<set_num;i++));
    do
        python run.py \
        --task game24 \
        --task_start_index $start_index \
        --task_end_index $end_index \
        --method_generate propose \
        --method_evaluate value \
        --method_select greedy \
        --n_evaluate_sample 3 \
        --n_select_sample ${array_b[i]} \
        --k ${array_k[i]} \
        --algorithm $algorithm \
        --name_of_task $today \
        #--graph_json # if use this is true
        ${@}
    done
done

for ((i=0;i<set_num;i++));
do
    python check_error_game24.py \
    --task game24 \
    --task_start_index $start_index \
    --task_end_index $end_index \
    --algorithm $algorithm \
    --n_select_sample ${array_b[i]} \
    --k ${array_k[i]} \
    --name_of_task $today
    ${@}    
done
