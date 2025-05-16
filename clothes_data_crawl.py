import json
import re
import sys

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

url1 = "https://www.gelato.com/blog/fabric-types"  # material
url2 = "https://www.bindboys.com/blog/100-clothing-types-every-fashion-enthusiast-must-know"  # type1
url3 = "https://www.clothingmanufacturersuk.com/post/types-of-jackets-a-comprehensive-guide"  # type2


def get_soup(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch URL: {url}\n{e}")
        sys.exit(1)


soup1 = get_soup(url1)
soup2 = get_soup(url2)
soup3 = get_soup(url3)


# def material titles
def material_title():
    main_title = soup1.find_all("h2", {"class": "mat-display-1 mat-display-1-md"})
    main_title2 = soup1.find_all("h2", {"class": "mat-display-1-md mat-display-2"})

    main_titles = []
    for tag in main_title:
        text = tag.get_text(strip=True)
        if text != "Next steps":
            main_titles.append(text)

    main_title2_texts = [tag.get_text(strip=True) for tag in main_title2][:2]
    all_titles = main_titles + main_title2_texts
    return all_titles


# def material list
def material_list():
    material_name = soup1.find_all("div", {"class": "text-p-black-100"})
    detail_type = []
    for name in material_name:
        h4s_with_span = name.find_all("h4")
        for h4 in h4s_with_span:
            span = h4.find("span")
            if span:
                text = span.get_text(strip=True)
                clean_text = re.sub(r"^\d+\.\s*", "", text)
                detail_type.append(clean_text)
    return detail_type


# def clothing types1
def type1_title():
    title = soup2.find_all("div", {"class": "post-description"})
    all_types = []
    for t in title:
        h4_tags = t.find_all("h4")
        for h4 in h4_tags:
            raw_text = h4.get_text(strip=True)
            clean = re.sub(r"^\d+\.\s*", "", raw_text)
            all_types.append(clean)
    return all_types


# def clothing types 2
def type2_title():
    small_title = soup3.find_all("p", {"class": "e3Vej UGrRC d-MNq GX0-h"})
    all_type = []
    for t in small_title:
        strong_tags = t.find_all("strong")
        for strong in strong_tags:
            style = strong.get("style", "")
            if "background-color" not in style:
                span = strong.find("span")
                if span:
                    text = span.get_text(strip=True)
                    if text:
                        cleaned = text.lstrip("-–• ").rstrip(":").strip()
                        all_type.append(cleaned)
    return all_type[15:-16]


if __name__ == "__main__":
    try:
        with tqdm(total=4, desc="Crawling Progress", ncols=80) as progress_bar:
            tqdm.write("[INFO] Crawling material list...")
            materials = material_list()
            progress_bar.update(1)
            progress_bar.refresh()

            tqdm.write("[INFO] Crawling clothing types from bindboys.com...")
            type1 = type1_title()
            progress_bar.update(1)
            progress_bar.refresh()

            tqdm.write(
                "[INFO] Crawling jacket types from clothingmanufacturersuk.com..."
            )
            type2 = type2_title()
            progress_bar.update(1)
            progress_bar.refresh()

            tqdm.write("[INFO] Saving JSON files...")
            with open("all_material_data.json", "w", encoding="utf-8") as f:
                json.dump(materials, f, ensure_ascii=False, indent=2)

            with open("all_clothing_types.json", "w", encoding="utf-8") as f:
                json.dump(type1 + type2, f, ensure_ascii=False, indent=2)

            progress_bar.update(1)
            progress_bar.refresh()

        tqdm.write("[SUCCESS] All data crawled and saved successfully.")

    except Exception as e:
        tqdm.write(f"[ERROR] Failed during crawling or saving: {e}")
        sys.exit(1)
