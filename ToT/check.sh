python check_error_game24.py \
    --task 'game24' \
    --task_start_index 900 \
    --task_end_index 901 \
    --algorithm 'whole_tree' \
    --n_select_sample 5 \
    --k 8 \
    --name_of_task $(date +%Y-%m-%d)
    ${@}