#!/usr/bin/python3

import subprocess
import tempfile
import typing

import yaml


def get_duplicates() -> typing.List[dict[str, str]]:
    duplicates = []
    already_exists = []
    tmp_path = tempfile.mkdtemp(dir='/tmp')
    elb_path = f'{tmp_path}/elb.yml'
    with open(elb_path, 'w') as f:
        ing_yml = subprocess.getoutput('kubectl get ingress proesc-homolog-ingress -o yaml')
        f.write(ing_yml)
    with open(elb_path, 'r') as f:
        elb = yaml.safe_load(f)
    
    for rule in elb['spec']['rules']:
        if rule['host'] in already_exists:
            duplicates.append(
                {
                    'release_name': rule['http']['paths'][0]['backend']['service']['name'],
                    'domain': rule['host']
                }
            )
            continue
        already_exists.append(rule['host'])
    
    return duplicates



def _handle_elb_files(domain: str, callback: typing.Callable[[typing.Any], typing.Any],
                      release_name: str or None = None, port_number: int or None = None, ) -> str:
    tmp_path = tempfile.mkdtemp(dir='/tmp')
    elb_path = f'{tmp_path}/elb.yml'
    with open(elb_path, 'w') as f:
        ing_yml = subprocess.getoutput('kubectl get ingress proesc-homolog-ingress -o yaml')
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

    modified_elb_path = _handle_elb_files(domain, callback, release_name, port_number)
    subprocess.call(['kubectl', 'replace', '-f', modified_elb_path])



def delete_entry_in_elb(domain: str) -> None:
    def callback(context: typing.Any) -> None:
        context['data']['spec']['rules'] = [x for x in context['data']['spec']['rules'] if
                                            x['host'] != context['domain']]
        return context

    modified_elb_path = _handle_elb_files(domain, callback=callback)
    subprocess.call(['kubectl', 'replace', '-f', modified_elb_path])


def main():
    duplicates = get_duplicates()
    for duplicate in duplicates:
        delete_entry_in_elb(duplicate['domain'])
        create_entry_in_elb(duplicate['release_name'], 8080, duplicate['domain'])


if __name__ == '__main__':
    main()
