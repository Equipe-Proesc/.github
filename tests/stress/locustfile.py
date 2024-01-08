

from locust import HttpUser, between, task


class Relatorios(HttpUser):
    wait_time = between(5, 10)

    @task
    def teste(self):
        self.login()
        self.client.get('pessoa/pessoas')

    # @task
    # def relatorio_pedagogico(self):
    #     ...

    def login(self):
        dados_login = {
            'usuario': 'matheusdantas@proesc.com',
            'senha': 'xxx',
        }

        self.client.post('login', data=dados_login)
