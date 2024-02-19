import json
import os
import pathlib
import sys

import jinja2
import urllib3


def update_testsigma_env(**kwargs) -> None:
    BASE_DIR = pathlib.Path(__file__).parent.parent
    templates_dir = f'{BASE_DIR}/templates'
    template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
    template_env = jinja2.Environment(loader=template_loader, autoescape=True)
    file_path = f'createTestsigmaEnv.json.j2'
    jinja_template = template_env.get_template(file_path)
    output = jinja_template.render(**kwargs)
    with open('envTestsigma.json', 'w') as f:
        f.write(output)


def get_kwargs() -> dict:
    args = sys.argv[2:]
    d = {}
    for arg in args:
        split = arg.split('=')
        d[split[0]] = ''.join(split[1:])
    return d


def update_testsigma() -> None:
    http = urllib3.PoolManager()
    with open('envTestsigma.json', 'r') as f:
        r = http.request(
            'POST',
            'https://app.testsigma.com/api/v1/environments',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(sys.argv[1])
            },
            body=f.read()
        )

        if r.status == 201:
            data = json.loads(r.data.decode('utf-8'))
            print(data['id'])
            return

    # TODO: Validar forma mais escalável
    page = 0
    r = http.request(
        'GET',
        f'https://app.testsigma.com/api/v1/environments',
        {'page': page},
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(sys.argv[1])
        },
    )

    while content := json.loads(r.data.decode('utf-8')).get('content'):
        for x in content:
            if x['name'] == 'CI - {}'.format(os.getenv('PR_NUMBER')):
                print(x['id'])
                return
        page += 1
        r = http.request(
            'GET',
            f'https://app.testsigma.com/api/v1/environments',
            {'page': page},
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(sys.argv[1])
            },
        )

    raise AssertionError('JSON does not follow interface')


def main() -> None:
    update_testsigma_env(**get_kwargs())
    update_testsigma()


if __name__ == '__main__':
    main()
