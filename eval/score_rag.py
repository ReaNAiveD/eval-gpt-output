import json
import os
import re

import numpy as np

from gpt_util import get_copilot

os.chdir('..')
file_name = 'test_kb.json'

prompt = json.load(open('resources/prompt/judge_4.json', 'r', encoding='utf-8'))
copilot = get_copilot(prompt)

qa_content = json.load(open(f'../cli-recommendation/API/tests/{file_name}', 'r', encoding='utf-8'))

errors = [[answer.get("errors") for answer in qa_content[question]] for question in qa_content]
errors = [e for es in errors for e in es]
error_num = len([e for e in errors if e])
no_error_num = len([e for e in errors if e == []])
total = len(errors)

print(f"Correct: {no_error_num}/{(error_num+no_error_num)}({no_error_num/(error_num+no_error_num)}%)")

durations = [[answer.get("duration") for answer in qa_content[question] if answer.get("errors") is not None] for question in qa_content]
durations = [d for ds in durations for d in ds]
print(f"Avg Duration: {sum(durations)/len(durations)} sec")
print(f"\tmid: {np.median(durations)}")
print(f"\t.75: {np.quantile(durations, .75)}")
print(f"\t.95: {np.quantile(durations, .95)}")
print(f"\t.99: {np.quantile(durations, .99)}")

tokens = [[answer.get("usage")['gpt-35-turbo-16k']['total_tokens'] for answer in qa_content[question] if answer.get("errors") is not None] for question in qa_content]
tokens = [t for ts in tokens for t in ts]
print(f"Avg Token Usage: {sum(tokens)/len(tokens)}")
print(f"\tmid: {np.median(tokens)}")
print(f"\t.75: {np.quantile(tokens, .75)}")
print(f"\t.95: {np.quantile(tokens, .95)}")
print(f"\t.99: {np.quantile(tokens, .99)}")

relevance_scores = []
correctness_scores = []
consistency_scores = []
comprehensive_scores = []

for q, answers in qa_content.items():
    for answer in answers:
        if 'scenario' in answer and answer["scenario"] and 'commandSet' in answer["scenario"]:
            a = {}
            score_text = copilot(f'Task: {q} \nCommand Set: {json.dumps(answer["scenario"]["commandSet"])}')
            answer['score_text'] = score_text
            answer['score'] = {}
            r_match = re.search(r'((Relevance score: )|(<Relevance score:> ))(?P<score>\d+)', score_text)
            if r_match:
                score = int(r_match.groupdict()['score'])
                answer['score']['relevance'] = score
                relevance_scores.append(score)
            cor_match = re.search(r'((Correctness score: )|(<Correctness score:> ))(?P<score>\d+)', score_text)
            if cor_match:
                score = int(cor_match.groupdict()['score'])
                answer['score']['correctness'] = score
                correctness_scores.append(score)
            con_match = re.search(r'((Consistency score: )|(<Consistency score:> ))(?P<score>\d+)', score_text)
            if con_match:
                score = int(con_match.groupdict()['score'])
                answer['score']['consistency'] = score
                consistency_scores.append(score)
            com_match = re.search(r'((Comprehensive score: )|(<Comprehensive score:> ))(?P<score>\d+)', score_text)
            if com_match:
                score = int(com_match.groupdict()['score'])
                answer['score']['comprehensive'] = score
                comprehensive_scores.append(score)
            with open(f'../cli-recommendation/API/tests/{file_name}', 'w', encoding='utf-8', newline='') as f:
                json.dump(qa_content, f, indent=4)
