from lib.app import app
import subprocess

from lib.core.helpers import delete_entry_in_elb, delete_dns_entry


@app.command()
def delete_ci_k8s(release_name: str, domain: str):
    if 'ci' not in release_name or 'ci.' not in domain:
        raise ValueError('Automação apenas suportada para ambientes de CI/CD')
    delete_dns_entry(domain)
    delete_entry_in_elb(domain)
    subprocess.call(['helm', 'uninstall', release_name])
