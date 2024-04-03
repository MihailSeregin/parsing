import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd


def parse_page(country_url: str):
    response = requests.get(country_url)
    soup = BeautifulSoup(response.content, "html.parser")
    country_data = {}
    for table_content in soup.find_all(class_="table-responsive"):
        country_data.update(parse_table(table_content))

    return country_data


def parse_table(table):
    table_data = {}
    for row in table.find_all("tr")[1:]:
        table_data.update(parse_row(row))
    return table_data


def parse_row(row):
    stadium_data = {}

    cols = row.find_all("td")
    first_col = cols[0].find("a")

    stadium_data["href"] = first_col["href"]
    stadium_data["stadium_name"] = first_col.text

    for i, col_name in enumerate(["City", "Clubs", "Capacity"]):
        stadium_data[col_name] = cols[i + 1].text.strip()
    return {first_col.text: stadium_data}


def get_urls(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")

    data = {}
    for group_countries in soup.find_all("ul", class_="country-list"):
        for li in group_countries.find_all("li"):
            href = li.find("a")["href"]
            text = li.find("a").text
            country, stadiums_number = text.split("(")

            data[country] = {"href": href, "stadiums_number": stadiums_number}

    return data


def parse_save():
    base_url = "http://stadiumdb.com/stadiums#AFC"
    country_hrefs = get_urls(base_url)
    country_stadium_data = {}

    for country in tqdm(country_hrefs):
        country_stadium_data[country] = parse_page(country_hrefs[country]["href"])

    df = pd.DataFrame(
        columns=["href", "stadium_name", "City", "Clubs", "Capacity", "Country"]
    )
    for country in country_stadium_data:
        country_data = country_stadium_data[country]
        for stadium_name in country_data:
            stadium_data = country_data[stadium_name]
            stadium_data["Country"] = country
            df = df.append(stadium_data, ignore_index=True)

    df.columns = ["href", "Name", "City", "Clubs", "Capacity", "Country"]
    df[["Name", "Clubs", "Capacity", "City", "Country", "href"]].to_excel(
        "Countries_stadiums.xlsx"
    )
