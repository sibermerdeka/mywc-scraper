# Source: https://github.com/junekomeiji/mywcscraper/blob/main/mywcscraper.py

import re
import requests
from bs4 import BeautifulSoup
from alive_progress import alive_bar

def toilet_info(URL: str):
    """
    Returns the information on a public toilet (tandas awam) given a MyWC URL.

    URL format: https://mywc.kpkt.gov.my/toilet/[location]
    """
    page = requests.get(URL, timeout=60)

    soup = BeautifulSoup(page.content, "html.parser")

    #find name of toilet
    h2 = str(soup.find_all("h2", class_="text-3xl font-extrabold text-gray-900"))
    name = re.findall("<h2[^>]*>([^<]+)</h2>", h2)

    #find address of toilet
    p = str(soup.findAll("p", class_="text-sm text-gray-500 truncate mb-2 uppercase flex flex-row"))
    address = re.findall("<span[^>]*>([^<]+)</span>", p)
    address[1] = address[1].capitalize()

    #find lat and long of toilet
    script = str(soup.find_all("script"))
    location = re.findall(".+?(?<=setView\(\[)(.\d*\.?\d*)\,(..\d*\.?\d*)", script)

    #rating
    span = str(soup.find_all("span", class_="text-sm"))
    rating = re.findall("\((.+?)\)", span)

    #facilities
    repg = str(soup.find_all("span", class_="px-2"))
    facilities = re.findall("<span[^>]*>([^<]+)</span>", repg)

    return {
        "url": URL,
        "name": name[0],
        "address": ''.join(address),
        "tags": ", ".join(facilities),
        "lat": location[0][0].strip(' '),
        "lng": location[0][1].strip(' '),
        "rating": rating[-1][0]
    }

def get_toilet_list(start_page: int = 0, n_pages: int = 515) -> list:
    """
    Returns a list of all toilet URLs currently in MyWC.

    Maximum number of pages is 515 as of 8 Aug 2024.
    """
    toilets = []

    for page_num in range(n_pages):
         # Access the nth MyWC page
        url = "https://mywc.kpkt.gov.my/?keyword=&state_id=&page={}#toilet-search-list".format(page_num)
        reqs = requests.get(url, timeout=60)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        # Find all URLs in that page, then filter to just toilet URLs
        links = soup.find_all('a')
        urls = [link.get('href') for link in links]
        toilet_filter = filter(lambda s: "https://mywc.kpkt.gov.my/toilet/" in s, urls)
        toilets += [t for t in toilet_filter]

    return toilets

def get_toilet_info(start_page: int = 0, n_pages: int = 515) -> dict:
    """
    Returns a dictionary of lists of information for the first `n_pages` pages of public toilets.

    Maximum number of pages is 515 as of 8 Aug 2024.
    """
    result = {
        "url": [],
        "name": [],
        "address": [],
        "tags": [],
        "lat": [],
        "lng": [],
        "rating": []
    }

    with alive_bar(n_pages * 10) as bar:
        for page_num in range(start_page, start_page + n_pages):
            # Access the nth MyWC page
            url = "https://mywc.kpkt.gov.my/?keyword=&state_id=&page={}#toilet-search-list".format(page_num)
            reqs = requests.get(url, timeout=60)
            soup = BeautifulSoup(reqs.text, 'html.parser')

            # Find all URLs in that page, then filter to just toilet URLs
            links = soup.find_all('a')
            urls = [link.get('href') for link in links]
            toilet_urls = filter(lambda s: "https://mywc.kpkt.gov.my/toilet/" in s, urls)

            for t in toilet_urls:
                t_info = toilet_info(t)
                result["url"].append(t_info["url"])
                result["name"].append(t_info["name"])
                result["address"].append(t_info["address"])
                result["tags"].append(t_info["tags"])
                result["lat"].append(t_info["lat"])
                result["lng"].append(t_info["lng"])
                result["rating"].append(t_info["rating"])
                bar()
        
        

    return result