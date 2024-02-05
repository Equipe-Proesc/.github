from typing import Dict
import base64

from lib.app import app


import yaml


@app.command()
def create_environment(
    name: str,
    kind: str = 'Secret',
    type: str = 'Opaque',
    output_path: str = 'environment.yml',
    data: str = "EXAMPLE='test'</>EXAMPLE2='@Anstruther'"
):
    with open(output_path, 'w') as f:
        f.write(yaml.dump([]))
    with open(output_path, 'w') as f:
        kwargs = data.split('</>')
        encoded_kwargs: Dict[str, str] = {}
        for kwarg in kwargs:
            key, value = kwarg.split('=', 1)
            encoded_kwargs[key] = value.strip("'")
        if kind == 'Secret':
            encoded_kwargs = {
                k: base64.b64encode(v.encode('utf-8')).decode('utf-8')
                for k, v in encoded_kwargs.items()
            }
        environment: Dict[str, str] = {
            'apiVersion': 'v1',
            'kind': kind,
            'metadata': {
                'name': name
            },
            'type': type,
            'data': encoded_kwargs
        }
        f.write(yaml.dump(environment))


if __name__ == '__main__':
    create_environment('teste', VAR_1='teste', VAR2='teste')  # noqa: E501
