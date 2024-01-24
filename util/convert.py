from cli_validator.result import CommandSetResult


def convert_command_set_result(result: CommandSetResult):
    out = {
        "items": [],
        "failures": [],
        "example_failures": [],
    }
    for item in result.items:
        json_item = {
            "signature": item.signature,
            "parameters": item.parameters,
            "example": item.example,
        }
        out["items"].append(json_item)
        if item.result:
            json_item["failure"] = item.result.msg
            out["failures"].append(json_item)
        if item.example_result:
            json_item["example_failure"] = item.example_result.msg
            out["example_failures"].append(json_item)
    return out
