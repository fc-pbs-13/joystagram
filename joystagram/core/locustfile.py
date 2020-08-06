from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(0.1, 0.2)

    @task
    def index_page(self):
        # self.client.get('/posts', headers={'Authorization': 'token 34339139d2d4eb06b7b3572faab7f3cb2176c0ca'})
        self.client.get('/users/locust_test',
                        headers={'Authorization': 'token 34339139d2d4eb06b7b3572faab7f3cb2176c0ca'})

    # def on_start(self):
    #     response = self.client.post('/login', data={'email': 'a@a.com', 'password': 1111})
