#!/usr/bin/bash

times=1
k=5
b=3
today=$(date +%Y-%m-%d)
start_index=900
end_index=1000
algorithm='whole_tree'

for ((i=1;i<=$times;i+=1))
do
    # k5b3
    k=5
    b=3
    python run.py \
    --task game24 \
    --task_start_index $start_index \
    --task_end_index $end_index \
    --method_generate propose \
    --method_evaluate value \
    --method_select greedy \
    --n_evaluate_sample 3 \
    --n_select_sample $b \
    --k $k \
    --algorithm $algorithm \
    --name_of_task $today
    ${@} \
    && python check_error_game24.py \
    --task game24 \
    --task_start_index $start_index \
    --task_end_index $end_index \
    --algorithm $algorithm \
    --n_select_sample $b \
    --k $k \
    --name_of_task $today
    ${@}

    # k8b5
    k=8
    b=5
    python run.py \
    --task game24 \
    --task_start_index $start_index \
    --task_end_index $end_index \
    --method_generate propose \
    --method_evaluate value \
    --method_select greedy \
    --n_evaluate_sample 3 \
    --n_select_sample $b \
    --k $k \
    --algorithm $algorithm \
    --name_of_task $today
    ${@} \
    && python check_error_game24.py \
    --task game24 \
    --task_start_index $start_index \
    --task_end_index $end_index \
    --algorithm $algorithm \
    --n_select_sample $b \
    --k $k \
    --name_of_task $today
    ${@}
done