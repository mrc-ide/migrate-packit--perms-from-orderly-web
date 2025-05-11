import montagu
import requests
from urllib.parse import urljoin

class OrderlyWebPermissions:
    def __init__(self, montagu_url, ow_url, user, password):
        print("initialising OrderlyWebPermissions")
        self.montagu_url = montagu_url
        self.ow_url = ow_url
        self.user = user
        self.password = password

    def authenticate(self):
        print("authenticating with Montagu")
        monty = montagu.MontaguAPI(self.montagu_url, self.user, self.password)
        token = monty.token
        print("token:")
        print(token)
        print("authenticating with OrderlyWeb")
        # make login call with montagu cookie set, and get ow cookie
        ow_login_url = self.ow_url + "/login/" # TODO: find a better join!
        print(ow_login_url)
        headers = { "Cookie": f"montagu_jwt_token={token}" }
        response = requests.get(ow_login_url, headers=headers, allow_redirects=False)
        print(response.text)
        self.cookie = response.headers["Set-Cookie"]
        print("ow-cookie:")
        print(self.cookie)

    def get(self,relative_url):
        url = self.ow_url + relative_url # TODO: find better goin
        headers = { "Cookie": self.cookie }
        response = requests.get(url, headers=headers)
        print(response.text)
        return response

    def get_roles(self):
        print("getting roles")
        response = self.get("/roles/")

    def get_users(self):
        print("getting users")
        response = self.get("/users/")


