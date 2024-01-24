import json
import logging
import time
from typing import List

from cli_validator import CLIValidator

logger = logging.getLogger(__name__)


def eval_scenario_gen(copilot, validator: CLIValidator, scenarios: List[str], **kwargs):
    lines = []
    for scenario in scenarios:
        logger.info("Scenario: " + scenario)
        scenario_result = {"scenario": scenario, "content": {}}
        start = time.time()
        try:
            if 'context' in kwargs:
                scenario += '\nHere are some potentially relevant commands information:\n' + \
                            '\n'.join(kwargs['context'])
            content = copilot(scenario)
            end = time.time()
            scenario_result["duration"] = end - start
            scenario_result["content"]["text"] = content
            content = json.loads(content)
            scenario_result["content"].update(content)
            command_set = content['commandSet']
            logging.info("CommandSet: " + str(command_set))
            result = validator.validate_command_set(command_set)
        except Exception as e:
            if "duration" not in scenario_result:
                scenario_result["duration"] = time.time() - start
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
    return lines


def eval_split_task(copilot, validator: CLIValidator, scenarios: List[str], **kwargs):
    reanswer = kwargs.get('reanswer')
    lines = []
    for scenario in scenarios:
        scenario = scenario.strip('\n')
        logging.info("Scenario: " + scenario)
        scenario_result = {"scenario": scenario, "content": {}}
        start = time.time()
        try:
            content = copilot(scenario)
            end = time.time()
            scenario_result["duration"] = end - start
            scenario_result["content"]["text"] = content
            tasks = json.loads(content)
            scenario_result["content"]["list"] = []
            logging.info("Tasks: " + str(tasks))
            for idx, task in enumerate(tasks):
                task_info = {
                    "task": task,
                }
                if task.startswith("az "):
                    parts = task.split(" -")
                    signature = parts[0].strip()
                    parameters = ["-{}".format(part).split()[0].strip() for part in parts[1:]]
                    failure = validator.validate_sig_params(signature, parameters)
                    if failure:
                        task_info["result"] = str(failure)
                else:
                    try:
                        content = reanswer("How to " + task)
                        if content.startswith("az "):
                            task_info["alter"] = content
                        else:
                            task_info["reanswered"] = content
                    except Exception as e:
                        task_info["reanswer_error"] = str(e)
                        logging.error("Single Command Copilot Error: " + str(e))
                scenario_result["content"]["list"].append(task_info)
        except Exception as e:
            if "duration" not in scenario_result:
                scenario_result["duration"] = time.time() - start
            scenario_result["error"] = str(e)
            logging.error("Error: " + str(e))
        finally:
            lines.append(scenario_result)
    return lines


def eval_full_desc_split_task(copilot, validator: CLIValidator, scenarios: List[str], **kwargs):
    reanswer = kwargs.get('reanswer')
    lines = []
    for scenario in scenarios:
        scenario = scenario.strip('\n')
        logging.info("Scenario: " + scenario)
        scenario_result = {"scenario": scenario, "content": {}}
        start = time.time()
        try:
            content = copilot(scenario)
            end = time.time()
            scenario_result["duration"] = end - start
            scenario_result["content"]["text"] = content
            tasks = json.loads(content)
            scenario_result["content"]["list"] = []
            logging.info("Tasks: " + str(tasks))
            for idx, task in enumerate(tasks):
                task_info = {
                    "task": task,
                }
                desc_command = task.split('||', 1)
                task_info['desc'] = desc_command[0]
                if len(desc_command) >= 2:
                    command = desc_command[1]
                    task_info['command'] = command
                    parts = command.split(" -")
                    signature = parts[0].strip()
                    parameters = ["-{}".format(part).split()[0].strip() for part in parts[1:]]
                    failure = validator.validate_sig_params(signature, parameters)
                    if failure:
                        task_info["result"] = str(failure)
                else:
                    try:
                        content = reanswer("How to " + desc_command[0])
                        if content.startswith("az "):
                            task_info["alter"] = content
                        else:
                            task_info["reanswered"] = content
                    except Exception as e:
                        task_info["reanswer_error"] = str(e)
                        logging.error("Single Command Copilot Error: " + str(e))
                scenario_result["content"]["list"].append(task_info)
        except Exception as e:
            if "duration" not in scenario_result:
                scenario_result["duration"] = time.time() - start
            scenario_result["error"] = str(e)
            logging.error("Error: " + str(e))
        finally:
            lines.append(scenario_result)
    return lines
