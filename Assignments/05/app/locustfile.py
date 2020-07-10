import random
from bs4 import BeautifulSoup
from locust import HttpUser, task, between


class User(HttpUser):
    wait_time = between(5, 10)

    @task
    def top_n_page(self):
        sub_url = '/top_n'
        response = self.client.get(sub_url)
        token = self._parse_csrf_token(response)
        data = self._packaging_data(token, top_n=random.randint(5, 10))
        response = self.client.post(sub_url, data)

    @task
    def distance_page(self):
        sub_url = '/distance'
        response = self.client.get(sub_url)
        token = self._parse_csrf_token(response)
        data = self._packaging_data(token,
                                    latitude=random.uniform(-90, 90),
                                    longitude=random.uniform(-180, 180),
                                    distance=random.randint(0, 10000))
        response = self.client.post(sub_url, data)

    @task
    def data_page(self):
        sub_url = '/date'
        response = self.client.get(sub_url)
        token = self._parse_csrf_token(response)
        date1 = random.randint(1, 15)
        date2 = random.randint(1, 15)
        start_date = '2020-06-' + str(min(date1, date2))
        end_date = '2020-06-' + str(max(date1, date2))
        data = self._packaging_data(token,
                                    start_date=start_date,
                                    end_date=end_date,
                                    magnitude=random.randint(0, 10))
        response = self.client.post(sub_url, data)

    @task
    def scale_page(self):
        sub_url = '/scale'
        response = self.client.get(sub_url)
        token = self._parse_csrf_token(response)
        mag1 = random.randint(1, 10)
        mag2 = random.randint(1, 10)
        data = self._packaging_data(token,
                                    recent_days=random.randint(20, 50),
                                    low_mag=min(mag1, mag2),
                                    high_mag=max(mag1, mag2))
        response = self.client.post(sub_url, data)

    @task
    def compare_page(self):
        sub_url = '/compare'
        response = self.client.get(sub_url)
        token = self._parse_csrf_token(response)
        data = self._packaging_data(token,
                                    loc1_latitude=random.uniform(-90, 90),
                                    loc1_longitude=random.uniform(-180, 180),
                                    loc2_latitude=random.uniform(-90, 90),
                                    loc2_longitude=random.uniform(-180, 180),
                                    distance=random.randint(0, 10000))
        response = self.client.post(sub_url, data)

    @task
    def largest_page(self):
        sub_url = '/largest'
        response = self.client.get(sub_url)
        token = self._parse_csrf_token(response)
        data = self._packaging_data(token,
                                    latitude=random.uniform(-90, 90),
                                    longitude=random.uniform(-180, 180),
                                    distance=random.randint(0, 10000))
        response = self.client.post(sub_url, data)

    def _parse_csrf_token(self, response):
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_token = soup.find('input', attrs={'name': 'csrf_token'})['value']
        return csrf_token

    def _packaging_data(self, csrf_token, **kwargs):
        data = {'csrf_token': csrf_token}
        for key in kwargs:
            data[key] = kwargs[key]
        data['submit'] = 'Submit'
        return data
