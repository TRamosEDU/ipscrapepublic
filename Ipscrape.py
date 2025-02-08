import requests
import csv
import os
import subprocess

url = "redacted"
response = requests.get(url)
data = response.json()

filename = 'ips.csv'
fieldname = 'Ips'

us_east_ips = []
for entry in data.get('prefixes', []):
    if entry.get('region') == 'us-east-1':
        us_east_ips.extend(entry.get('ip_prefix', []))

print(us_east_ips)

existing_values = set()
file_exists = os.path.isfile(filename)
print(file_exists)

if file_exists:
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file)
        if reader.fieldnames:
            existing_values = {row[fieldname] for row in reader}

new_unique_values = [value for value in us_east_ips if value not in existing_values]

if new_unique_values:
    with open(filename, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[fieldname])
        if file.tell() == 0:
            writer.writeheader()
        for value in new_unique_values:
            writer.writerow({fieldname: value})
            # Add new IP to iptables
            subprocess.run([
                'sudo', 'iptables', '-A', 'INPUT',
                '-s', value,
                '-j', 'DROP',
                '-m', 'comment', '--comment', 'IPScrape'
            ], check=False)

# Remove IPs from iptables that are in CSV but not in current list
ips_to_remove = existing_values - set(us_east_ips)
for ip in ips_to_remove:
    subprocess.run([
        'sudo', 'iptables', '-D', 'INPUT',
        '-s', ip,
        '-j', 'DROP',
        '-m', 'comment', '--comment', 'IPScrape'
    ], check=False)
