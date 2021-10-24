import shutil
from os.path import join, dirname, abspath
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from PIL import Image

from normalize import normalize

BASE_URL = "https://wiki.teamfortress.com"
LIST_OF_MAPS_URL = "/wiki/Template:List_of_maps"

failed_downloads = []


def get(url, stream=False):
    response = requests.get(BASE_URL + url, stream=stream)
    if response.status_code != 200:
        print(f"Error getting {url}, got {response.status_code}")
        failed_downloads.append(url)
        return True, None
    return False, response


def pad(value):
    return f"{value:.<60}"


def main():
    err, response = get(LIST_OF_MAPS_URL)
    if err:
        exit(1)

    list_soup = BeautifulSoup(response.text, "html.parser")

    map_table_entries = list_soup.find(
        "table", "wikitable").tbody.findAll("tr")

    for entry in map_table_entries[1:]:
        map_page_url = entry.find("b").a["href"]
        map_name = entry.find("code").next

        print(f"Getting thumbnail of {map_name}...")

        print(pad(f"➤ Reading map page {map_page_url}"), end="")

        err, response = get(map_page_url)
        if err:
            continue
        print(response.status_code)

        map_page_soup = BeautifulSoup(response.text, "html.parser")
        img_page_url = map_page_soup.find("table", "infobox").tbody\
            .findChildren("tr")[1].find("a")["href"]
        filename = f"{map_name}.jpg"

        try:
            destination = open(
                join(dirname(abspath(__file__)), "img", filename), "xb+")
        except FileExistsError:
            print(f"➤ File {filename} exists, skipping.")
            continue

        print(pad(f"➤ Reading image page {img_page_url}"), end="")

        err, response = get(img_page_url)
        if err:
            continue
        print(response.status_code)

        img_page_soup = BeautifulSoup(response.text, "html.parser")
        img_url = img_page_soup.find("div", "fullImageLink").find("a")["href"]

        print(pad(f"➤ Reading image {img_url}"), end="")

        err, response = get(img_url, stream=True)
        if err:
            continue
        print(response.status_code)

        print("➤ Normalizing image...")
        b_io = BytesIO()
        shutil.copyfileobj(response.raw, b_io)
        img = Image.open(b_io)
        img_normalized = normalize(img)

        print(f"➤ Writing image to {filename}")
        img_normalized.save(destination)

    if len(failed_downloads) != 0:
        print("Done, but these downloads failed:")
        for err in failed_downloads:
            print(err)
    else:
        print("Done, no errors.")


if __name__ == "__main__":
    main()
