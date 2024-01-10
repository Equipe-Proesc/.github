

from locust import HttpUser, between, task


class Relatorios(HttpUser):
    wait_time = between(1, 5)

    @task
    def teste(self):
        self.login_inovadados()
        self.client.get('pessoa/pessoas', verify=False)

    # @task
    # def relatorio_pedagogico(self):
    #     ...

    def login_inovadados(self):
        login_data = {
            '_token': 'W1JpHewZbOfHcxKLEqEBr4I5R2f7rjCcaLg1xJz9',
            'email': 'matheusdantas@proesc.com',
            'password': 'senhaSuperSeguraOficial', # não é a senha verdadeira <3
            'dispositivo_login': 'app',
            'nome_codigo': None
        }

        self.client.post('login', data=login_data, verify=False)

        self.client.get('save-autenticacao', data={
            'pessoaId': '539439',
            'entidade_id': '1',
            'unidade_id': '1'
        })
