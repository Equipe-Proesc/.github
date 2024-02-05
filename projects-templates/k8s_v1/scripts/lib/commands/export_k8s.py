import subprocess
import pathlib

from lib.app import app
from lib.core.constants import is_production_flags


@app.command()
def export_k8s(
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
        '--dry-run',
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

    subprocess.call(args)
