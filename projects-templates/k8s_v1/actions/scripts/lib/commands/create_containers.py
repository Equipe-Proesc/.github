from typing import Optional, Dict
import os

import yaml

from lib.app import app


@app.command()
def create_containers(
    name: str,
    image: str,
    port: int = 0,
    env_from_secret: str = 'no-env',
    healthcheck_path: Optional[str] = None,
    healthcheck_port: Optional[int] = None,
    requests_cpu: str = '100m',
    requests_mem: str = '214Mi',
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
            'resources': {
                'requests': {
                    'cpu': requests_cpu,
                    'memory': requests_mem
                }
            }
        }

        if env_from_secret != 'no-env':
            container['envFrom'] = [
                {
                    'secretRef': {
                        'name': env_from_secret
                    }
                }
            ]

        if port != 0:
            container['ports'] = [
                {
                    'name': 'http',
                    'containerPort': port,
                    'protocol': 'TCP'
                }
            ]

        if healthcheck_path:
            container['readinessProbe'] = {
                'httpGet': {
                    'port': healthcheck_port if healthcheck_port else port,
                    'path': healthcheck_path
                }
            }

        f.write(yaml.dump([*actual_containers, container]))


if __name__ == '__main__':
    create_containers('teste', 'teste', 8080, 'secret-ref', '/health-check-custom', None, '1000m', '1Gib', 'Always')  # noqa: E501
