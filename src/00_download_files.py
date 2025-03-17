# %%
import pandas as pd
import requests
from urllib.parse import urlparse
import logging

logging.basicConfig(
    filename="logs/01.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

# %%
html_links = pd.read_parquet("../data/plan_files.parquet")
html_links = html_links[html_links.verwijzingNaarTekst.str.contains("/t_")].reset_index(
    drop=True
)

html_links = set(html_links.verwijzingNaarTekst.to_list())
# %%

dir_ = "../data/plan_documents/"
for url in html_links:
    try:
        response = requests.get(url)
        response.raise_for_status()

        parsed_url = urlparse(url)
        webpage_name = parsed_url.path.strip("/").split("/")[-1] or "index.html"
        webpage_name = dir_ + "/" + webpage_name

        if "pdf" in webpage_name:
            with open(file=webpage_name, mode="wb") as file:
                file.write(response.content)
        else:
            with open(file=webpage_name, mode="w", encoding="utf-8") as file:
                file.write(response.text)

        print(f"The website content has been saved to {webpage_name}")
    except requests.RequestException as e:
        print(f"An error occurred while fetching the webpage: {e}")
# %%
