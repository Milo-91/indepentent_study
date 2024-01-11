# 5-shot
standard_prompt = '''Use numbers and basic arithmetic operations (+ - * /) to obtain 24.
Input: 4 4 6 8
Answer: (4 + 8) * (6 - 4) = 24
Input: 2 9 10 12
Answer: 2 * 12 * (10 - 9) = 24
Input: 4 9 10 13
Answer: (13 - 9) * (10 - 4) = 24
Input: 1 4 8 8
Answer: (8 / 4 + 1) * 8 = 24
Input: 5 5 5 9
Answer: 5 + 5 + 5 + 9 = 24
Input: {input}
'''

# 5-shot
cot_prompt = '''Use numbers and basic arithmetic operations (+ - * /) to obtain 24. Each step, you are only allowed to choose two of the remaining numbers to obtain a new number.
Input: 4 4 6 8
Steps:
4 + 8 = 12 (left: 4 6 12)
6 - 4 = 2 (left: 2 12)
2 * 12 = 24 (left: 24)
Answer: (6 - 4) * (4 + 8) = 24
Input: 2 9 10 12
Steps:
12 * 2 = 24 (left: 9 10 24)
10 - 9 = 1 (left: 1 24)
24 * 1 = 24 (left: 24)
Answer: (12 * 2) * (10 - 9) = 24
Input: 4 9 10 13
Steps:
13 - 10 = 3 (left: 3 4 9)
9 - 3 = 6 (left: 4 6)
4 * 6 = 24 (left: 24)
Answer: 4 * (9 - (13 - 10)) = 24
Input: 1 4 8 8
Steps:
8 / 4 = 2 (left: 1 2 8)
1 + 2 = 3 (left: 3 8)
3 * 8 = 24 (left: 24)
Answer: (1 + 8 / 4) * 8 = 24
Input: 5 5 5 9
Steps:
5 + 5 = 10 (left: 5 9 10)
10 + 5 = 15 (left: 9 15)
15 + 9 = 24 (left: 24)
Answer: ((5 + 5) + 5) + 9 = 24
Input: {input}
'''

# 1-shot
propose_prompt = '''Generate only one set of below output
Input: 2 8 8 14
8 Possible next steps:
2 + 8 = 10
8 / 2 = 4
14 + 2 = 16
2 * 8 = 16
8 - 2 = 6
14 - 8 = 6
14 /  2 = 7
14 - 2 = 12

Input: 2 8 14
5 Possible next steps:
2 + 8 = 10
14 - 8 = 6
14 + 2 = 16
8 / 2 = 4
2 - 8 = -6

Input: 10 14
3 Possible next steps:
10 + 14 = 24
10 - 14 = -4
10 * 14 = 140

Input: {input}
{k} Possible next steps:
'''

value_prompt = '''Evaluate if given numbers can reach 24 (sure/likely/impossible)
sure means these numbers or this number can reach 24
likely means these numbers or this number have or has the probability to reach 24
impossible means these numbers or this number can't reach 24
below are several sets of examples, and you can generate only one set of the below examples according to the Input
Output must be sure, likely, or impossible, choose one
Input: 4 4 10
Analysis:
4 + 4 + 10 = 8 + 10 = 18
4 * 10 - 4 = 40 - 4 = 36
(10 - 4) * 4 = 6 * 4 = 24
Output: sure (4 4 10)

Input: 4 9 11
Analysis:
9 + 11 + 4 = 20 + 4 = 24
Output: sure (4 9 11)

Input: 5 7 8
Analysis:
5 + 7 + 8 = 12 + 8 = 20
(8 - 5) * 7 = 3 * 7 = 21
I cannot obtain 24 now, but the numbers are within a reasonable range
Output: likely (5 7 8)

Input: 5 6 6
Analysis:
5 + 6 + 6 = 17
(6 - 5) * 6 = 1 * 6 = 6
I cannot obtain 24 now, but the numbers are within a reasonable range
Output: likely (5 6 6)

Input: 10 10 11
Analysis:
10 + 10 + 11 = 31
(11 - 10) * 10 = 10
10 10 10 are all too big
Output: impossible (10 10 11)

Input: 1 3 3
Analysis:
1 * 3 * 3 = 9
(1 + 3) * 3 = 12
1 3 3 are all too small
Output: impossible (1 3 3)

Input: 0 4 6
Analysis:
0 + 4 + 6 = 10
0 * 4 * 6 = 0
0 + 4 * 6 = 24
Output: sure (0 4 6)

Input: 10 14
Analysis:
10 + 14 = 24
Output: sure (10 14)

Input: 24 0
Analysis:
24 + 0 = 24 
Output: sure (24 0)

Input: 11 12
Analysis:
11 + 12 = 23
12 - 11 = 1
11 * 12 = 132
11 / 12 = 0.91
Output: impossible (11 12)

Input: 24
Analysis:
24 is equal to 24
Output: sure (24)

Input: 10
Analysis:
10 is not equal to 24
Output: impossible (10)

Input: -1
Analysis:
-1 is not equal to 24
Output: impossible (-1)

Input: {input}
'''

value_last_step_prompt = '''Use numbers and basic arithmetic operations (+ - * /) to obtain 24. Given an input and an answer, give a judgement (sure/impossible) if the answer is correct, i.e. it uses each input exactly once and no other numbers, and reach 24.
Input: 4 4 6 8
Answer: (4 + 8) * (6 - 4) = 24
Judge: 
sure
Input: 2 9 10 12
Answer: 2 * 12 * (10 - 9) = 24
Judge: 
sure
Input: 4 9 10 13
Answer: (13 - 9) * (10 - 4) = 24
Judge: 
sure
Input: 4 4 6 8
Answer: (4 + 8) * (6 - 4) + 1 = 25
Judge: 
impossible
Input: 2 9 10 12
Answer: 2 * (12 - 10) = 24
Judge: 
impossible
Input: 4 9 10 13
Answer: (13 - 4) * (10 - 9) = 24
Judge: 
impossible
Input: {input}
Answer: {answer}
Judge:'''