import requests
import csv
import os

# URL containing the JSON data
url = "redacted"

# Fetch JSON data from the URL
response = requests.get(url)
data = response.json()

filename = 'ips.csv'
fieldname = 'Ips'

# Extract IP prefixes for us-east-1
us_east_ips = []
for entry in data.get('prefixes', []):
    if entry.get('region') == 'us-east-1':
        # Extend the list with all IP prefixes from this entry
        us_east_ips.extend(entry.get('ip_prefix', []))

# Print the result
print(us_east_ips)

# Read existing values from CSV (if it exists)
existing_values = set()
file_exists = os.path.isfile(filename)
print(file_exists)

if file_exists:
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file)
        if reader.fieldnames:  # Check if header exists
            existing_values = {row[fieldname] for row in reader}

# Determine new unique values to add
new_unique_values = [value for value in us_east_ips if value not in existing_values]

# Append new values to CSV (with header if file is empty/new)
if new_unique_values:
    with open(filename, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[fieldname])
        # Write header only if the file is empty/new
        if file.tell() == 0:  # Check if file position is at 0 (empty)
            writer.writeheader()
        # Write new rows
        for value in new_unique_values:
            writer.writerow({fieldname: value})