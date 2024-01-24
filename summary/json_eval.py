import numpy as np


def summary_json_eval(eval_data):
    all_commands = []
    durations = []
    non_error_durations = []
    errors = []
    scenario_with_exceptions = set()
    command_non_az = []
    scenario_with_exceptions_with_az = set()
    unknown_command = []
    unrecognized_arguments = []
    missing_required = []
    invalid_value = []
    other_failure = []
    for scenario in eval_data:
        if 'duration' in scenario:
            durations.append(scenario['duration'])
        if 'error' in scenario:
            errors.append(scenario['scenario'])
            continue
        elif 'duration' in scenario:
            non_error_durations.append(scenario['duration'])
        for command in scenario['content']['commandSet']:
            all_commands.append(command)
            if 'example_failure' in command:
                scenario_with_exceptions.add(scenario['scenario'])
                if "The input command is not an Azure CLI command." in command['example_failure']:
                    command_non_az.append(command)
                else:
                    scenario_with_exceptions_with_az.add(scenario['scenario'])
                    if "Unknown Command" in command['example_failure']:
                        unknown_command.append(command)
                    elif "unrecognized arguments" in command['example_failure']:
                        unrecognized_arguments.append(command)
                    elif "the following arguments are required" in command["example_failure"]:
                        missing_required.append(command)
                    elif ": invalid " in command["example_failure"]:
                        invalid_value.append(command)
                    else:
                        other_failure.append(command)
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
        'non_az_command_num': len(command_non_az),
        'non_az_commands': [cmd['example'] for cmd in command_non_az],
        'unknown_command_num': len(unknown_command),
        'unrecognized_arguments_num': len(unrecognized_arguments),
        'missing_required_num': len(missing_required),
        'invalid_value_num': len(invalid_value),
        'other_failure_num': len(other_failure),
        'unknown_command': [cmd['example_failure'] for cmd in unknown_command],
        'unrecognized_arguments': [cmd['example_failure'] for cmd in unrecognized_arguments],
        'missing_required': [cmd['example_failure'] for cmd in missing_required],
        'invalid_value': [cmd['example_failure'] for cmd in invalid_value],
        'other_failure': [cmd['example_failure'] for cmd in other_failure],
        'failed_scenario_num': len(scenario_with_exceptions_with_az),
        'failed_scenarios': list(scenario_with_exceptions_with_az),
        'failed_scenario_num(include non-az)': len(scenario_with_exceptions),
        'failed_scenarios(include non-az)': list(scenario_with_exceptions),
    }
