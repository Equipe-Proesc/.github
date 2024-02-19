import json
import logging
import os
import time

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


def main() -> None:
    http = urllib3.PoolManager()
    curr_url = 'https://{}.ci.proesc.com/login'.format(os.getenv('PR_NUMBER'))

    counter = 0
    error_counter = 0
    while (
            curr_status := http.request(
                'GET',
                curr_url,
                headers={
                    'x-proesc-waf': os.getenv('WAF_BYPASS_TOKEN', 'None')
                }
            ).status
    ) != 200:
        try:
            logging.warning('Environment {} not ready yet'.format(curr_url))
            logging.warning('Current status: {}'.format(curr_status))
            counter += 1
            if counter == 30:  # para totalizar 5 minutos (300 segundos)
                send_slack_message(
                    'Erro na geração do ambiente: {}\nStatus do erro: {}\n<!subteam^S04UU2T0H2S>'
                    .format(curr_url, curr_status),
                    'tech')
                raise AssertionError('Ambiente não está pronto')
            time.sleep(10)
        except urllib3.exceptions.MaxRetryError:
            logging.warning('DNS of environment {} not propagated yet')
            error_counter += 1
            if error_counter == 60:  # para totalizar 10 minutos (300 segundos)
                send_slack_message(
                    'Erro na conexão com o ambiente devido ao DNS: {}\n<!subteam^S04UU2T0H2S>'.format(curr_url),
                    'tech_interno'
                )
                raise AssertionError('Ambiente não está recebendo conexões')
            time.sleep(10)

    logging.info('Environment ready: {}'.format(curr_url))


if __name__ == '__main__':
    main()
