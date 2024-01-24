import asyncio
import difflib
import json
import logging

from cli_validator import CLIValidator

from eval import eval_scenario_gen, eval_split_task, eval_full_desc_split_task
from gpt_util.copilot import get_copilot
from summary import summary_json_eval, summary_atomic_task_eval

logging.basicConfig(level=logging.INFO)


TOOLCHAINS = {
    'commandset': (eval_scenario_gen, summary_json_eval),
    'atomic_task': (eval_split_task, summary_atomic_task_eval),
    'full_desc_atomic_task': (eval_full_desc_split_task, summary_atomic_task_eval),
}


def load_kb(toolchain, file_name):
    _, summary_fn = TOOLCHAINS[toolchain]
    with open(f'resources/out/{file_name}', 'r') as f:
        eval_result = json.load(f)
    summary = summary_fn(eval_result)
    return {}, eval_result, summary


def eval_copilot(prompt_name, validator, scenarios, file_name):
    with open(f'resources/prompt/{prompt_name}.json', 'r') as f:
        prompt = json.load(f)
        # copilot = get_copilot(prompt)
    eval_fn, summary_fn = TOOLCHAINS[prompt['toolchain']]
    # kwargs = {}
    # if prompt['toolchain'] in ['atomic_task', 'full_desc_atomic_task']:
    #     with open(f'resources/prompt/reanswer4.json', 'r') as f:
    #         prompt_reanswer = json.load(f)
    #         copilot_reanswer = get_copilot(prompt_reanswer)
    #         kwargs['reanswer'] = copilot_reanswer
    # eval_result = eval_fn(copilot, validator, scenarios, **kwargs)
    # with open(f'resources/out/{file_name}', 'w', newline='') as f:
    #     json.dump(eval_result, f, indent=4)
    with open(f'resources/out/{file_name}', 'r') as f:
        eval_result = json.load(f)
    summary = summary_fn(eval_result)
    return prompt, eval_result, summary


def eval_scenario_and_compare(prompt_name1, prompt_name2, scenario):
    validator = CLIValidator()
    asyncio.run(validator.load_metas_async())
    with open(f'resources/scenarios/{scenario}.txt', 'r') as f:
        scenarios = [s.strip('\n') for s in f.readlines() if s.strip('\n')]
    prompt1, eval_result1, summary1 \
        = eval_copilot(prompt_name1, validator, scenarios, f'eval_p{prompt_name1}_s{scenario}.json')
    toolchain = prompt1['toolchain']
    if prompt_name2 == '' and scenario == 'kb':
        prompt2, eval_result2, summary2 = load_kb(toolchain, f'eval_skb_{toolchain}.json')
        prompt_name2 = 'kb'
    else:
        prompt2, eval_result2, summary2 \
            = eval_copilot(prompt_name2, validator, scenarios, f'eval_p{prompt_name2}_s{scenario}.json')

    differ = difflib.HtmlDiff(tabsize=4, wrapcolumn=80)
    tables = [
        differ.make_table(json.dumps(prompt1, indent=4).splitlines(), json.dumps(prompt2, indent=4).splitlines(), f'prompt {prompt_name1}', f'prompt {prompt_name2}'),
        differ.make_table(json.dumps(summary1, indent=4).splitlines(), json.dumps(summary2, indent=4).splitlines())
    ]
    for idx in range(len(eval_result1)):
        tables.append(differ.make_table(
            json.dumps(eval_result1[idx], indent=4).splitlines(),
            json.dumps(eval_result2[idx], indent=4).splitlines()))
    html = (differ._file_template % dict(
            styles=differ._styles,
            legend=differ._legend,
            table='\n'.join(tables),
            charset='utf-8'
        )).encode('utf-8', 'xmlcharrefreplace').decode('utf-8')
    with open(f'resources/out/diff_p{prompt_name1}_p{prompt_name2}_s{scenario}.html', 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == '__main__':
    # validator = CLIValidator()
    # asyncio.run(validator.load_metas_async())
    # with open(f'resources/scenarios/kb.txt', 'r') as f:
    #     scenarios = [s.strip('\n') for s in f.readlines() if s.strip('\n')]
    # eval_copilot('full_desc_atomic_task_35', validator, scenarios, f'eval_pfull_desc_atomic_task_35_skb.json')
    eval_scenario_and_compare('full_desc_atomic_task_35', 'atomic_task_35', 'kb')
