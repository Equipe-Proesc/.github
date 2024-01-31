from typing import Dict

from lib.app import app


import yaml


@app.command()
def create_environment(
    name: str,
    kind: str = 'Secret',
    type: str = 'Opaque',
    output_path: str = 'environment.yml',
    **kwargs
):
    with open(output_path, 'w') as f:
        f.write(yaml.dump([]))
    with open(output_path, 'w') as f:
        environment: Dict[str, str] = {
            'apiVersion': 'v1',
            'kind': kind,
            'metadata': {
                'name': name
            },
            'type': type,
            'data': kwargs
        }
        f.write(yaml.dump(environment))


if __name__ == '__main__':
    create_environment('teste', VAR_1='teste', VAR2='teste')  # noqa: E501
