import requests


if __name__ == '__main__':
    auth = {'Authorization': 'api_secret_key'}
    data = {'name': 'FastAPI Man'}
    r = requests.get('http://127.0.0.1:8000/test', params=data, headers=auth)
    if r.status_code == 200:
        print(r.json())
    else:
        print(r.content)
