import json
import urllib.request
import urllib.error
from datetime import datetime
from urllib.parse import quote

filename = "requirements.txt"

dependencies_checked = 0
packages_not_found = 0
versions_not_found = 0
oldest_release = None

def get_json(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise

with open(filename, "r", encoding="utf-8") as file:
    lines = [line.strip() for line in file if line.strip()]

dependencies_checked = len(lines)

for line in lines:
    if "==" in line:
        name, version = line.split("==", 1)
    else:
        name = line
        version = None

    name = name.strip()
    name_url = quote(name, safe="")

    package_data = get_json(
        f"https://pypi.org/pypi/{name_url}/json"
    )

    if package_data is None:
        packages_not_found += 1
        continue

    if version is None:
        continue

    version_url = quote(version.strip(), safe="")
    release_data = get_json(
        f"https://pypi.org/pypi/{name_url}/{version_url}/json"
    )

    if release_data is None:
        versions_not_found += 1
        continue

    urls = release_data.get("urls", [])

    if not urls:
        continue

    upload_time = urls[0].get("upload_time")

    if not upload_time:
        continue

    release_date = datetime.fromisoformat(
        upload_time.replace("Z", "+00:00")
    )

    if oldest_release is None or release_date < oldest_release["date"]:
        oldest_release = {
            "date": release_date,
            "name": name,
            "version": version.strip()
        }

print(f"Dependencies checked: {dependencies_checked}")
print(f"Packages not on PyPI: {packages_not_found}")
print(f"Versions not on PyPI: {versions_not_found}")

if oldest_release:
    print(
        f"Oldest pinned release: "
        f"{oldest_release['name']}=={oldest_release['version']} "
        f"({oldest_release['date'].year})"
    )
else:
    print("Oldest pinned release: None")