from migrate_packit_perms_from_orderly_web.orderly_web_permissions import OrderlyWebPermissions

montagu_url = "https://localhost/api"
ow_url = "https://localhost/reports"
disable_verify = True
password = "password"

print("logging in dev user")
dev_perms = OrderlyWebPermissions(montagu_url, ow_url, "dev.user@example.com", password, disable_verify=True)
dev_perms.authenticate()

print("logging in funder user")
funder_perms = OrderlyWebPermissions(montagu_url, ow_url, "funder.user@example.com", password, disable_verify=True)
funder_perms.authenticate()

print("logging in admin user")
admin_perms = OrderlyWebPermissions(montagu_url, ow_url, "admin.user@example.com", password, disable_verify=True)
admin_perms.authenticate()