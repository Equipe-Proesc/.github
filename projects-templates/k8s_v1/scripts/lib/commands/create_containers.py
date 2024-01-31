from typing import Optional, Dict
import os

import yaml

from lib.app import app


@app.command()
def create_containers(
    name: str,
    image: str,
    port: int,
    env_from_secret: str,
    healthcheck_path: Optional[str] = None,
    healthcheck_port: Optional[int] = None,
    requests_cpu: str = '100m',
    requests_mem: str = '214Mib',
    image_pull_policy: str = 'IfNotPresent',
    output_path: str = 'containers.yml',
    override: bool = False
):
    if override or not os.path.exists(output_path):
        with open(output_path, 'w') as f:
            f.write(yaml.dump([]))
    with open(output_path, 'r') as f:
        actual_containers = yaml.safe_load(f)
        if actual_containers is None:
            actual_containers = []
    with open(output_path, 'w') as f:
        container: Dict[str, str] = {
            'name': name,
            'image': image,
            'imagePullPolicy': image_pull_policy,
            'port': port,
            'readinessProbe': {
                'httpGet': {
                    'port': healthcheck_port if healthcheck_port else port,
                    'path': healthcheck_path if healthcheck_path else '/health-check'  # noqa: E501
                }
            },
            'ports': [
                {
                    'name': 'http',
                    'containerPort': port,
                    'protocol': 'TCP'
                }
            ],
            'envFrom': [
                {
                    'secretRef': {
                        'name': env_from_secret
                    }
                }
            ],
            'resources': {
                'requests': {
                    'cpu': requests_cpu,
                    'memeory': requests_mem
                }
            }
        }
        f.write(yaml.dump([*actual_containers, container]))


if __name__ == '__main__':
    create_containers('teste', 'teste', 8080, 'secret-ref', '/health-check-custom', None, '1000m', '1Gib', 'Always')  # noqa: E501
