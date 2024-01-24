import re
import numpy as np


def summary_atomic_task_eval(eval_data):
    all_commands = []
    durations = []
    non_error_durations = []
    errors = []
    out_of_scope = []
    non_az = []
    alters = []
    unknown_command = []
    unrecognized_arguments = []
    missing_required = []
    invalid_value = []
    other_failure = []
    scenario_with_exceptions = set()
    scenario_with_non_az = set()
    for scenario in eval_data:
        if 'duration' in scenario:
            durations.append(scenario['duration'])
        if scenario.get('content', {}).get('text') == 'Sorry, this question is out of my scope.':
            out_of_scope.append(scenario['scenario'])
            continue
        if 'error' in scenario:
            errors.append(scenario['scenario'])
            continue
        elif 'duration' in scenario:
            non_error_durations.append(scenario['duration'])
        for task in scenario['content']['list']:
            all_commands.append(task)
            if 'result' in task:
                scenario_with_exceptions.add(scenario['scenario'])
                if "Unknown Command" in task['result']:
                    unknown_command.append(task)
                elif "unrecognized arguments" in task['result']:
                    unrecognized_arguments.append(task)
                elif "the following arguments are required" in task["result"]:
                    missing_required.append(task)
                elif ": invalid " in task["result"]:
                    invalid_value.append(task)
                else:
                    other_failure.append(task)
            if re.match(r'^(kubectl )|(git )|(docker )', task['task']):
                scenario_with_non_az.add(scenario['scenario'])
                non_az.append(task)
            elif 'alter' in task:
                alters.append(task)
    return {
        'duration': {
            "avg": np.average(durations),
            "std": np.std(durations),
            "mid": np.median(durations),
            ".75": np.quantile(durations, .75),
            ".9": np.quantile(durations, .9),
            ".99": np.quantile(durations, .99), },
        'non_error_duration': {
            "avg": np.average(non_error_durations),
            "std": np.std(non_error_durations),
            "mid": np.median(non_error_durations),
            ".75": np.quantile(non_error_durations, .75),
            ".9": np.quantile(non_error_durations, .9),
            ".99": np.quantile(non_error_durations, .99), },
        'scenario_num': len(eval_data),
        'command_num': len(all_commands),
        'generation_errors_num': len(errors),
        'generation_errors': errors,
        'out_of_scope_num': len(out_of_scope),
        'out_of_scope': out_of_scope,
        'non_az_command_num': len(non_az),
        'non_az_commands': [cmd['task'] for cmd in non_az],
        'alter_command_num': len(alters),
        'alter_commands': alters,
        'unknown_command_num': len(unknown_command),
        'unrecognized_arguments_num': len(unrecognized_arguments),
        'missing_required_num': len(missing_required),
        'invalid_value_num': len(invalid_value),
        'other_failure_num': len(other_failure),
        'unknown_command': [cmd['result'] for cmd in unknown_command],
        'unrecognized_arguments': [cmd['result'] for cmd in unrecognized_arguments],
        'missing_required': [cmd['result'] for cmd in missing_required],
        'invalid_value': [cmd['result'] for cmd in invalid_value],
        'other_failure': [cmd['result'] for cmd in other_failure],
        'failed_scenario_num': len(scenario_with_exceptions),
        'failed_scenarios': list(scenario_with_exceptions),
    }
