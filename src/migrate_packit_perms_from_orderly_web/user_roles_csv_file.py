import csv;

class UserRolesCsvFile:
    def __init__(self):
        self.rows = []

    def add_row(self, user, role):
        self.rows.append({
            "user": user,
            "role": role
        })

    def write(self, file_name):
        with open(file_name, "w", newline='') as csv_file:
            field_names = ["user", "role"]
            writer = csv.DictWriter(csv_file, field_names)
            writer.writeheader()
            for row in self.rows:
                writer.writerow(row)