import csv;

class PermissionsCsvFile:
    def __init__(self):
        self.rows = []

    def add_row(self, permission_owner, source, permission, scope):
        self.rows.append({
            "permission_owner": permission_owner,
            "source": source,
            "permission": permission,
            "scope": scope
        })

    def write(self, file_name):
        with open(file_name, "w", newline='') as csv_file:
            field_names = ["permission_owner", "source", "permission", "scope"]
            writer = csv.DictWriter(csv_file, field_names)
            writer.writeheader()
            for row in self.rows:
                writer.writerow(row)