import pathlib
import subprocess

from lib.core.constants import is_production_flags
from lib.app import app


@app.command()
def deploy_k8s(
    release_name: str,
    service_port: int,
    service_type: str = 'NodePort',
    replica_count: int = 1,
    is_production: bool = False,
    environment_path: str = 'environments.yml',
    containers_path: str = 'containers.yml'
):
    args = [
        'helm',
        'upgrade',
        '--set', f'"replicaCount={replica_count}"',
        '--set', f'"service.type={service_type}"',
        '--set', f'"service.port={service_port}"',
        '--set', f'"service.type={service_type}"',
        '--set', f'"environmentPath={environment_path}"',
        '--set', f'"containersPath={containers_path}"',
        release_name,
        pathlib.Path(
            f'{pathlib.Path(__file__).parent.parent.parent.parent}/helm')
    ]

    if is_production:
        for flag in is_production_flags:
            args.insert(-2, flag)

    if release_name.startswith('ci-'):
        args.insert(2, '--install')

    subprocess.call(args)
