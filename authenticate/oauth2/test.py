import requests

if __name__ == '__main__':
    header = {
        'accept': "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    username = 'one'
    password = 'secret_one'

    payload = f"grant_type=password&client_id=&client_secret=&username={username}&password={password}"
    r = requests.post('http://127.0.0.1:8000/token', data=payload, headers=header)
    if r.status_code == 200:
        print(r.json())
    else:
        print(r.content)

