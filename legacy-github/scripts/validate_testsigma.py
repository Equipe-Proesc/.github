import json
import logging
import os
import pathlib

import urllib3


def send_slack_message(message: str, channel: str) -> None:
    h = urllib3.PoolManager()

    if channel == 'tech':
        url = 'https://hooks.slack.com/services/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'
    elif channel == 'geral':
        url = 'https://hooks.slack.com/services/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'
    elif channel == 'tech_interno':
        url = 'https://hooks.slack.com/services/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'
    else:
        logging.warning('Canal não encontrado, redirecionando para tech_interno')
        url = 'https://hooks.slack.com/services/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'

    body = json.dumps({'text': message}).encode('utf-8')
    r = h.request('POST', url, body=body)
    if r.status != 200:
        logging.warning('Feedback ao Slack não enviado')


def validate_testsigma() -> str:
    try:
        root_dir = pathlib.Path(__file__).parent.parent.parent
        testsigma_path = '{}/testsigma.json'.format(root_dir)
        with open(testsigma_path, 'r') as f:
            testsigma_result = json.load(f)
        return testsigma_result.get('consolidatedResult')
    except FileNotFoundError:
        return 'NO_TESTS'


def main() -> None:
    result = validate_testsigma()

    if result == 'FAILURE':
        send_slack_message(
            'Houve um erro nos testes do ambiente {}\nAutor da PR: {}'.format(os.getenv('APP_URL'),
                                                                              os.getenv('DEVELOPER_USERNAME')), 'tech')
        raise AssertionError('Houve uma falha no CI/CD')
    elif result == 'STOPPED':
        send_slack_message(
            'Testes cancelados no ambiente {}\nAutor da PR: {}'.format(os.getenv('APP_URL'),
                                                                       os.getenv('DEVELOPER_USERNAME')), 'tech')
        raise AssertionError('CI/CD interrompido')
    elif result == 'SUCCESS':
        print('Testes deram certo')
    elif result == 'NO_TESTS':
        print('Testes não foram executados')
    else:
        raise AssertionError('Status do Testsigma desconhecido')


if __name__ == '__main__':
    main()
