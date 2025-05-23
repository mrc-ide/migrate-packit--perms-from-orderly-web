import requests
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
            msg = 'Unexpected status code: {}. Unable to authenticate with montagu.'  # TODO: share response validate code
            raise Exception(msg.format(response.status_code))
        self.montagu_token = response.json()['access_token']
        print("token:")
        print(self.montagu_token)

        print("authenticating with OrderlyWeb")
        # make login call with montagu cookie set, and get ow cookie
        ow_login_url = self.ow_url + "/login/" # TODO: find a better join!
        print(ow_login_url)
        headers = { "Cookie": f"montagu_jwt_token={self.montagu_token}" }
        response = requests.get(ow_login_url, headers=headers, allow_redirects=False, verify = self.verify)
        if response.status_code != 302:
            msg = 'Unexpected status code: {}. Unable to authenticate with OrderlyWeb.'  # TODO: share response validate code
            raise Exception(msg.format(response.status_code))
        print(response.text)
        self.cookie = response.headers["Set-Cookie"]
        print("ow-cookie:")
        print(self.cookie)

    def get(self,relative_url):
        url = self.ow_url + relative_url # TODO: find better join
        print(f"Getting from: {url}")
        headers = {
            "Cookie": self.cookie,
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, verify = self.verify)
        print(response.text)
        # TODO: throww if not 200
        return response.json()["data"]

    def get_roles(self):
        print("getting OW roles")
        response = self.get("/roles/")
        return response

    def get_users(self):
        print("getting OW users")
        response = self.get("/users/")
        return response

    def get_published_report_versions(self):
        print("getting published OW report versions")
        response = self.get("/api/v2/versions/")
        result = {}
        for version in response:
            name = version["name"]
            id = version["id"]
            published = version["published"]
            # return a value in dict for each report even if no published versions
            if not name in result:
                result[name] = []
            if published:
                result[name].append(id)
        print("PUBLISHED VERSIONS")
        print(result)
        return result



