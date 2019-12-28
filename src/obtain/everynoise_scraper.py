# FUNCTIONS TO GET GENRES AND PLAYLIST LINKS FROM EVERY-NOISE-AT-ONCE

import functools
import os
import pickle
import re
import requests

from metis.readwrite import load_or_make

from bs4 import BeautifulSoup


# TODO:
# Turn src into a module and move load_or_make into another directory


@load_or_make
def scrape_all_links(domain, path, target_pattern):
    """
    Scrapes a website and compiles a list of urls that match a target pattern.
    
    Inputs: 
    - domain: domain of the website you want to scrape
    - path: path to the page that you want to scrape from `domain`
    - target_pattern: regex that specifies the types of links you want to collect
    
    Outputs:
    - target_urls: list of all the links on domain/path that match target_pattern
    """
    main_page = '/'.join(['http:/', domain, path])
    response = requests.get(main_page)

    if response.status_code != 200:
        raise ConnectionError(f"Failed to connect to {main_page}.")

    soup = BeautifulSoup(response.text, "lxml")

    target_regex = re.compile(target_pattern)
    target_urls = ['/'.join(['http:/', domain, x['href']])
                    for x in soup.find_all('a', {'href':target_regex})]

    return target_urls

@load_or_make
def scrape_links_from_each_page(urls, target_pattern, labeler=(lambda x:x)):
    """
    Loops over a list of urls and finds links that matches a target pattern from each page.
    
    Inputs:
    - urls: the list of urls to scrape links from
    - target_pattern: regex that specifies the types of links you want to collect
    - labeler: function that parses a url and returns a label for that page
    
    Outputs:
    - links: a dictionary with key/value pairs {url_label:[scraped_links]}
    """
    links = {}

    for url in urls:
        response = requests.get(url)
        label = labeler(url)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to connect to {url}.")

        soup = BeautifulSoup(response.text, "lxml")

        target_regex = re.compile(target_pattern)
        target_urls = [x['href'] for x in soup.find_all('a', {'href':target_regex})]

        links[label] = target_urls
    
    return links