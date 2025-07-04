import requests
import json

class PackitPermissions:
    def __init__(self, packit_api_url, disable_verify=False):
        self.packit_api_url = packit_api_url
        self.verify = not disable_verify

    def authenticate(self, montagu_token):
        print("authenticating with Packit")
        packit_login_url = f"{self.packit_api_url}/auth/login/montagu"
        headers = { "Authorization": f"Bearer {montagu_token}" }
        response = requests.get(packit_login_url, headers = headers, verify = self.verify)
        if response.status_code != 200:
            msg = 'Unexpected status code: {}. Unable to authenticate with Packit.'
            raise Exception(msg.format(response.status_code))
        self.access_token = response.json()["token"]

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
        headers["Content-Type"] = "application/json"
        response = requests.put(url, data = json.dumps(data), headers = headers, verify = self.verify)
        if response.status_code != 200:
            raise Exception(f"Unexpected status code {response.status_code} for PUT {url}")

    def delete(self, relative_url):
        url = self.get_url(relative_url)
        headers = self.get_auth_header()
        response = requests.delete(url, headers = headers, verify = self.verify)
        if response.status_code != 204:
            raise Exception(f"Unexpected status code {response.status_code} for DELETE {url}")

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

    def delete_role(self, role_name):
        self.delete(f"/roles/{role_name}")

    # This is used both to set permissions on user group roles, and individual user roles (identified by user name)
    def set_permissions_on_role(self, role_name, permissions):
        self.put(f"/roles/{role_name}/permissions", {
            "addPermissions": permissions,
            "removePermissions": []
        })

    # This is used to check if packets referenced in scoped permissions (including those relevant to published report
    # permissions actually exist in packit). If not, this may indicate a problem with report migration. If any do not
    # exist, remove from list of packets to set permissions for, and return these separately
    def check_packets_exist(self, packets_by_group):
        nonexistent = []
        for packet_group, ids in packets_by_group.items():
            print(f"checking {packet_group}...")
            to_remove = []
            for id in ids:
                 url = self.get_url(f"/packets/{id}")
                 headers = self.get_auth_header()
                 response = requests.get(url, headers=headers, verify = self.verify)
                 if response.status_code == 404 or response.status_code == 400:
                     to_remove.append(id)
                     nonexistent.append({"packet_group": packet_group, "id": id})
                 elif response.status_code != 200:
                     raise Exception(f"Unexpected status code {response.status_code} on packet check")
            for id in to_remove:
                ids.remove(id)
        return nonexistent


