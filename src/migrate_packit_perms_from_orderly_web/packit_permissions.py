import requests

class PackitPermissions:
    def __init__(self, packit_url, disable_verify=False):
        print("initialising PackitPermissions")
        self.packit_url = packit_url
        self.verify = not disable_verify

    def authenticate(self, montagu_token):
        print("authenticating with Packit, montagu token is " + montagu_token)
        packit_login_url = f"{self.packit_url}/auth/login/montagu"
        headers = { "Authorization": f"Bearer {montagu_token}" }
        response = requests.get(packit_login_url, headers = headers, verify = self.verify)
        if response.status_code != 200:
            msg = 'Unexpected status code: {}. Unable to authenticate with Packit.'  # TODO: share response validate code
            raise Exception(msg.format(response.status_code))
        self.access_token = response.json()["token"]
        print(f"Packit token: {self.access_token}")