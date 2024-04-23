from ruamel.yaml import YAML # type: ignore

def extract_inputs(cwl_filename):
    yaml = YAML()

    with open(cwl_filename, 'r') as f:
        cwl = yaml.load(f)

    for element in cwl['$graph']:
        if element['class'] == 'Workflow':
            return element['inputs']

    return None