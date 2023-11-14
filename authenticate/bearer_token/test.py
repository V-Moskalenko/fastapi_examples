import requests


if __name__ == '__main__':
    user = {'username': 'one', 'password': 'secret_one'}
    r = requests.post('http://127.0.0.1:8000/token', params=user)
    if r.status_code == 200:
        token = r.json()['access_token']
        header = {'Authorization': f'Bearer {token}'}

        data = {'name': 'FastAPI Man'}
        new_r = requests.get('http://127.0.0.1:8000/test', params=data, headers=header)
        print(new_r.json())
    else:
        print(r.content)