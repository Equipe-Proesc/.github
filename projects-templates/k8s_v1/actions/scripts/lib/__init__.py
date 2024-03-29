# flake8: noqa

def start():
    from lib.commands.add_ci_k8s_dns import add_ci_k8s_dns
    from lib.commands.create_containers import create_containers
    from lib.commands.create_environment import create_environment
    from lib.commands.delete_ci_k8s import delete_ci_k8s
    from lib.commands.deploy_k8s import deploy_k8s
    from lib.commands.export_k8s import export_k8s
    from lib.config import app_name, version
    from lib.app import app
