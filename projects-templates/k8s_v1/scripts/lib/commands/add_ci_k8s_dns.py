from lib.app import app

from lib.core.helpers import create_dns_entry, create_entry_in_elb


@app.command()
def add_ci_k8s_dns(release_name: str, port_number: int, domain: str):
    if 'ci' not in release_name or 'ci.' not in domain:
        raise ValueError('Automação apenas suportada para ambientes de CI/CD')
    create_entry_in_elb(release_name, port_number, domain)
    create_dns_entry(domain)
