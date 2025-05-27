import requests
import json

class PackitPermissions:
    def __init__(self, packit_api_url, disable_verify=False):
        print("initialising PackitPermissions")
        self.packit_api_url = packit_api_url
        self.verify = not disable_verify

    def authenticate(self, montagu_token):
        print("authenticating with Packit, montagu token is " + montagu_token)
        packit_login_url = f"{self.packit_api_url}/auth/login/montagu"
        headers = { "Authorization": f"Bearer {montagu_token}" }
        response = requests.get(packit_login_url, headers = headers, verify = self.verify)
        if response.status_code != 200:
            msg = 'Unexpected status code: {}. Unable to authenticate with Packit.'  # TODO: share response validate code
            raise Exception(msg.format(response.status_code))
        self.access_token = response.json()["token"]
        print(f"Packit token: {self.access_token}")

    def get_auth_header(self):
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    def get_url(self, relative_url):
        return f"{self.packit_api_url}{relative_url}"

    def get(self,relative_url):
        url = self.get_url(relative_url)
        headers = self.get_auth_header()
        headers["Accept"] = "application/json"
        response = requests.get(url, headers=headers, verify = self.verify)
        if response.status_code != 200:
            raise Exception(f"Unexpected status code {response.status_code} for GET {url}")
        return response.json()

    def post(self, relative_url, data):
        url = self.get_url(relative_url)
        headers = self.get_auth_header()
        headers["Content-Type"] = "application/json"
        response = requests.post(url, data = json.dumps(data), headers = headers, verify = self.verify)
        if response.status_code != 201:
            raise Exception(f"Unexpected status code {response.status_code} for POST {url}")

    def put(self, relative_url, data):
        url = self.get_url(relative_url)
        headers = self.get_auth_header()
        headers["Content-Type"] = "application/json" # TODO: be more DRY
        response = requests.put(url, data = json.dumps(data), headers = headers, verify = self.verify)
        if response.status_code != 200:
            raise Exception(f"Unexpected status code {response.status_code} for PUT {url}")

    def get_users(self):
        print("Getting Packit users")
        return self.get("/users")

    def get_roles(self):
        print("Getting Packit roles")
        return self.get("/roles")

    def create_user(self, username, email, display_name, user_roles):
        self.post("/user/external", {
            "username": username,
            "email": email,
            "displayName": display_name,
            "userRoles": user_roles
        })

    def create_role(self, role_name):
        self.post("/roles", {
            "name": role_name,
            "permissionNames": [] # permissions are set in a separate call
        })

    # This is used both to set permissions on user group roles, and individual user roles (identified by user name)
    def set_permissions_on_role(self, role_name, permissions):
        self.put(f"/roles/{role_name}/permissions", {
            "addPermissions": permissions,
            "removePermissions": []
        })
