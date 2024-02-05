from lib.app import app


@app.command()
def deploy_k8s(
    release_name: str,
    docker_uri: str,
    is_production: bool = False,
    environment_path: str = 'environments.yml',
    containers_path: str = 'containers.yml'
):
    ...
