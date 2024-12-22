import shutil
from os.path import join, dirname, abspath
from io import BytesIO
import re

import requests
from bs4 import BeautifulSoup
from PIL import Image

from normalize import normalize

BASE_URL = "https://wiki.teamfortress.com"
LIST_OF_MAPS_URL = "/wiki/Template:List_of_maps"

TARGET_RES_W = 320
TARGET_RES_H = 180

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


def normalize_map_name(name):
    map_suffix_regex = re.compile(
        "^(final\\d*|rc\\d+[a-z]*|rcx|[a-z]\\d+[a-z]*|[a-z]|beta\\d+[a-z]*|nb\\d+|fix)$"
    )

    return "_".join(
        map(
            lambda i_and_name_part: i_and_name_part[1],
            filter(
                lambda i_and_name_part: not (
                    i_and_name_part[0] > 1
                    and map_suffix_regex.fullmatch(i_and_name_part[1])
                ),
                enumerate(name.lower().split("_")),
            ),
        )
    )


def main():
    err, response = get(LIST_OF_MAPS_URL)
    if err:
        exit(1)

    list_soup = BeautifulSoup(response.text, "html.parser")

    map_table_entries = list_soup.find("table", "wikitable").tbody.findAll("tr")

    for entry in map_table_entries[1:]:
        map_page_url = entry.find("img").parent["href"]
        map_name = entry.find("code").next

        print(f"Getting thumbnail of {map_name}...")

        print(pad(f"➤ Reading map page {map_page_url}"), end="")

        err, response = get(map_page_url)
        if err:
            continue
        print(response.status_code)

        map_page_soup = BeautifulSoup(response.text, "html.parser")
        img_page_url = (
            map_page_soup.find("table", "infobox")
            .tbody.findChildren("tr")[1]
            .find("a")["href"]
        )
        filename = f"{normalize_map_name(map_name)}.png"

        try:
            destination = open(join(dirname(abspath(__file__)), "img", filename), "xb+")
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
        img_normalized = normalize(img, target_size=(TARGET_RES_W, TARGET_RES_H))

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
