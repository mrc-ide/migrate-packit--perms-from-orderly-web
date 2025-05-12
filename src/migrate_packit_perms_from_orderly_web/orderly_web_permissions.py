import requests
import os
from urllib.parse import urljoin

class OrderlyWebPermissions:
    def __init__(self, montagu_url, ow_url, user, password, disable_verify=False):
        print("initialising OrderlyWebPermissions")
        self.montagu_url = montagu_url
        self.ow_url = ow_url
        self.user = user
        self.password = password
        self.verify = not disable_verify


    def authenticate(self):
        print("authenticating with Montagu")
        auth_url = f"{self.montagu_url}/v1/authenticate/"
        data = 'grant_type=client_credentials'
        auth = (self.user, self.password)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(auth_url, data=data, auth=auth,
                                 headers=headers, verify = self.verify)
        if response.status_code != 200:
            msg = 'Unexpected status code: {}. Unable to authenticate.'
            raise Exception(msg.format(response.status_code))
        token = response.json()['access_token']
        print("token:")
        print(token)

        print("authenticating with OrderlyWeb")
        # make login call with montagu cookie set, and get ow cookie
        ow_login_url = self.ow_url + "/login/" # TODO: find a better join!
        print(ow_login_url)
        headers = { "Cookie": f"montagu_jwt_token={token}" }
        response = requests.get(ow_login_url, headers=headers, allow_redirects=False, verify = self.verify)
        print(response.text)
        self.cookie = response.headers["Set-Cookie"]
        print("ow-cookie:")
        print(self.cookie)

    def get(self,relative_url):
        url = self.ow_url + relative_url # TODO: find better join
        print(f"Getting from: {url}")
        headers = { "Cookie": self.cookie }
        response = requests.get(url, headers=headers, verify = self.verify)
        print(response.text)
        return response

    def get_roles(self):
        print("getting roles")
        response = self.get("/roles/")
        print(response.text)
        return response

    def get_users(self):
        print("getting users")
        response = self.get("/users/")
        print(response.text)
        return response


