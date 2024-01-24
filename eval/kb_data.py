import asyncio
import json
import logging
import os

import azure.cosmos.cosmos_client as cosmos_client
from cli_validator import CLIValidator


logger = logging.getLogger(__name__)


def scenario_container():
    client = cosmos_client.CosmosClient(
        'https://cli-recommendation.documents.azure.com:443/',
        {'masterKey': os.environ['COSMOS_KEY']})
    db = client.get_database_client('cli-recommendation')
    return db.get_container_client('e2e-scenario-online')


def fetch_kb_scenario():
    container = scenario_container()
    query_str = 'select * from c'
    scenarios = container.query_items(query_str, enable_cross_partition_query=True)
    with open('resources/out/skb.json', 'w+', encoding='utf-8', newline='') as f:
        json.dump(list(scenarios), f, indent=4)


def reformat_commandset_and_eval():
    validator = CLIValidator()
    asyncio.run(validator.load_metas_async())
    with open('resources/out/skb.json', 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    lines = []
    for scenario in scenarios:
        scenario_result = {"scenario": scenario['description'], "content": scenario}
        try:
            command_set = scenario['commandSet']
            result = validator.validate_command_set(command_set)
        except Exception as e:
            scenario_result["error"] = str(e)
            logger.error("Error: " + str(e))
        else:
            for idx, item in enumerate(result.items):
                if item.result:
                    scenario_result["content"]["commandSet"][idx]['failure'] = item.result.msg
                if item.example_result:
                    scenario_result["content"]["commandSet"][idx]['example_failure'] = item.example_result.msg
        finally:
            lines.append(scenario_result)
    with open('resources/out/eval_skb_commandset.json', 'w+', encoding='utf-8', newline='') as f:
        json.dump(list(lines), f, indent=4)


def reformat_atomic_task_and_eval():
    validator = CLIValidator()
    asyncio.run(validator.load_metas_async())
    with open('resources/out/skb.json', 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    lines = []
    for scenario in scenarios:
        scenario_result = {"scenario": scenario['description'], "content": {}}
        try:
            scenario_result["content"]["list"] = []
            for idx, command in enumerate(scenario['commandSet']):
                task = f'{command["command"]} {" ".join(command["arguments"])}'
                task_info = {
                    "task": task,
                }
                failure = validator.validate_sig_params(command["command"], command["arguments"])
                if failure:
                    task_info["result"] = str(failure)
                scenario_result["content"]["list"].append(task_info)
        except Exception as e:
            scenario_result["error"] = str(e)
            logging.error("Error: " + str(e))
        finally:
            lines.append(scenario_result)
    with open('resources/out/eval_skb_atomic_task.json', 'w+', encoding='utf-8', newline='') as f:
        json.dump(list(lines), f, indent=4)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reformat_atomic_task_and_eval()
