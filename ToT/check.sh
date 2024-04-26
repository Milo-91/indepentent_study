python check_error_game24.py \
    --task 'game24' \
    --task_start_index 900 \
    --task_end_index 910 \
    --algorithm 'whole_tree' \
    --n_select_sample 3 \
    --k 5 \
    --name_of_task $(date +%Y-%m-%d)
    ${@}