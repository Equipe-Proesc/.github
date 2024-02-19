#!/usr/bin/python3

import enum
import optparse
import subprocess
import tempfile
import typing

import boto3
import yaml

# Github Actions deve ter as garantias de:
#  - rodar sempre a partir da master
#  - colocar o env certo para rodar deploy


class Action(enum.Enum):
    CREATE = 'create'
    DELETE = 'delete'


class ScriptArguments(typing.Dict):
    domain: str
    image_version: str
    repository: str
    release_name: str
    action: Action
    port_number: str
    is_stress_test: str


def _get_elb_endpoint() -> str:
    endpoint = subprocess.getoutput(
        'kubectl get ingress proesc-homolog-ingress -o=jsonpath={.status.loadBalancer.ingress[0].hostname}'
    )
    return endpoint


def _handle_elb_files(domain: str, callback: typing.Callable[[typing.Any], typing.Any],
                      release_name: str or None = None, port_number: int or None = None, ) -> str:
    tmp_path = tempfile.mkdtemp(dir='/tmp')
    elb_path = f'{tmp_path}/elb.yml'
    with open(elb_path, 'w') as f:
        ing_yml = subprocess.getoutput(
            'kubectl get ingress proesc-homolog-ingress -o yaml')
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


def get_arguments() -> ScriptArguments:
    parser = optparse.OptionParser()
    parser.add_option('-d', '--domain', dest='domain')
    parser.add_option('-r', '--repository', dest='repository')
    parser.add_option('-i', '--image', dest='image_version')
    parser.add_option('-n', '--release-name', dest='release_name')
    parser.add_option('-a', '--action', dest='action')
    parser.add_option('-p', '--port', dest='port_number')
    parser.add_option('-s', '--stress-test', dest='is_stress_test')
    (options, arguments) = parser.parse_args()

    action = options.action

    if not action:
        parser.error('[-] Missing action to do')

    if (
            (action == Action.CREATE.value and not (
                options.domain and options.image_version and options.repository and options.release_name and options.port_number
            )) or
            (action == Action.DELETE.value and not (
                options.release_name and options.domain
            ))
    ):
        parser.error('[-] Missing required param')

    if '.ci.proesc.com' not in options.domain:
        raise ValueError('Cannot update non CI domain')

    return options


def create_environment_in_k8s(release_name: str, repository: str, image_version: str, is_stress_test: typing.Optional[str] = 'false') -> None:
    subprocess.call([
        'k8s/scripts/deploy.sh',
        '',
        release_name,
        repository,
        image_version,
        'default',
        'false',
        'false',
        is_stress_test if is_stress_test else 'false'
    ])


def delete_environment_in_k8s(release_name: str) -> None:
    subprocess.call(['helm', 'uninstall', release_name])


def create_entry_in_elb(release_name: str, port_number: int, domain: str) -> None:
    def callback(context: typing.Any) -> None:
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


def delete_entry_in_elb(domain: str) -> None:
    def callback(context: typing.Any) -> None:
        context['data']['spec']['rules'] = [x for x in context['data']['spec']['rules'] if
                                            x['host'] != context['domain']]
        return context

    modified_elb_path = _handle_elb_files(domain, callback=callback)
    subprocess.call(['kubectl', 'replace', '-f', modified_elb_path])


def create_dns_entry(elb_endpoint: str, domain: str) -> None:
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
                                    'Value': elb_endpoint
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
        import logging
        logging.error(e)
        logging.warning('POSSIBLY ROUTE ALREADY CREATED NOT CHANGING ANYTHING')


def delete_dns_entry(elb_endpoint: str, domain: str):
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
                                'Value': elb_endpoint
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


def main():
    options = get_arguments()
    elb_endpoint = _get_elb_endpoint()

    if options.action == Action.CREATE.value:
        create_environment_in_k8s(
            options.release_name, options.repository, options.image_version, options.is_stress_test)
        create_entry_in_elb(options.release_name, int(
            options.port_number), options.domain)
        create_dns_entry(elb_endpoint, options.domain)
        return

    delete_dns_entry(elb_endpoint, options.domain)
    delete_entry_in_elb(options.domain)
    delete_environment_in_k8s(options.release_name)


if __name__ == '__main__':
    main()
