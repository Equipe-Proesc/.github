from typing import Callable, Any, Optional
import tempfile
import subprocess
import traceback

import yaml
import boto3

ingress_name = 'proesc-homolog-ingress'


def _get_elb_endpoint() -> str:
    endpoint = subprocess.getoutput(
        f'kubectl get ingress {ingress_name} -o=jsonpath={{.status.loadBalancer.ingress[0].hostname}}'  # noqa: E501
    )
    return endpoint


def _handle_elb_files(domain: str, callback: Callable[[Any], Any],
                      release_name: Optional[str] = None,
                      port_number: Optional[int] = None) -> str:
    tmp_path = tempfile.mkdtemp(dir='/tmp')
    elb_path = f'{tmp_path}/elb.yml'
    with open(elb_path, 'w') as f:
        ing_yml = subprocess.getoutput(
            f'kubectl get ingress {ingress_name} -o yaml')
        f.write(ing_yml)
    with open(elb_path, 'r') as f:
        elb = yaml.safe_load(f)
    modified_elb_path = f'{tmp_path}/modified-elb.yml'
    context = {
        'domain': domain,
        'release_name': release_name,
        'port_number': port_number,
        'data': elb
    }
    elb = callback(context)['data']
    with open(modified_elb_path, 'w') as f:
        yaml.dump(elb, f)
    return modified_elb_path


def create_entry_in_elb(release_name: str, port_number: int,
                        domain: str) -> None:
    def callback(context: Any) -> None:
        found = False
        for rule in context['data']['spec']['rules']:
            if rule['host'] == context['domain']:
                found = True
                break

        if not found:
            context['data']['spec']['rules'].append({
                'host': context['domain'],
                'http': {
                    'paths': [
                        {
                            'backend': {
                                'service': {
                                    'name': context['release_name'],
                                    'port': {
                                        'number': context['port_number']
                                    }
                                }
                            },
                            'path': '/',
                            'pathType': 'Prefix'
                        }
                    ]
                }
            })
        return context

    modified_elb_path = _handle_elb_files(
        domain, callback, release_name, port_number)
    subprocess.call(['kubectl', 'replace', '-f', modified_elb_path])


def create_dns_entry(domain: str) -> None:
    try:
        route53 = boto3.client('route53')
        route53.change_resource_record_sets(
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': domain,
                            'ResourceRecords': [
                                {
                                    'Value': _get_elb_endpoint()
                                }
                            ],
                            'TTL': 3600,
                            'Type': 'CNAME'
                        }
                    }
                ],
                'Comment': 'Creating CI/CD environment'
            },
            HostedZoneId='Z093676329LYG4DZ505OD'
        )
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        print('Rota possivelmente já existe, não foram feitas modificações')


def delete_entry_in_elb(domain: str) -> None:
    def callback(context: Any) -> None:
        context['data']['spec']['rules'] = [x for x in context['data']['spec']['rules'] if x['host'] != context['domain']]  # noqa: E501
        return context

    modified_elb_path = _handle_elb_files(domain, callback=callback)
    subprocess.call(['kubectl', 'replace', '-f', modified_elb_path])


def delete_dns_entry(domain: str):
    route53 = boto3.client('route53')
    route53.change_resource_record_sets(
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': domain,
                        'ResourceRecords': [
                            {
                                'Value': _get_elb_endpoint()
                            }
                        ],
                        'TTL': 3600,
                        'Type': 'CNAME'
                    }
                }
            ],
            'Comment': 'Deleting CI/CD environment'
        },
        HostedZoneId='Z093676329LYG4DZ505OD'
    )
