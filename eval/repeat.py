import asyncio
import json
import logging
from typing import List

from cli_validator import CLIValidator

from eval import eval_scenario_gen
from gpt_util import get_copilot
from summary.json_eval import summary_json_eval


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def repeat_eval_scenario_gen(prompt_name, scenarios: List[str], count=20):
    validator = CLIValidator()
    asyncio.run(validator.load_metas_async())
    with open(f'resources/prompt/{prompt_name}.json', 'r') as f:
        prompt = json.load(f)
        copilot = get_copilot(prompt)
    result = []
    for i in range(count):
        logger.info(f'Running {i+1}/{count}')
        result.append(eval_scenario_gen(copilot, validator, scenarios))
    for scenario_result in zip(*result):
        summary = summary_json_eval(list(scenario_result))
        with open(f'resources/out/p{prompt_name}_s{scenario_result[0]["scenario"].replace(" ", "_")}.json', 'w',
                  encoding='utf-8', newline='') as f:
            json.dump({
                "summary": summary,
                "result": result
            }, f, indent=4)


if __name__ == "__main__":
    repeat_eval_scenario_gen('commandset_4', ['Configure NAT gateway for Azure Container Instances workloads that use the NAT gateway\'s public IP address for static egress'])
