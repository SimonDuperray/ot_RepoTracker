import pandas as pd
import numpy as np 
import requests
from bs4 import BeautifulSoup
import json
from IPython.display import display

def get_repositories(url, headers):
    return requests.get(url, headers=headers).json()

def get_repositories_names(repositories_list):
    repositories_names = []
    for item in repositories_list:
        repositories_names.append(item['name'])
    return repositories_names

def get_dict_repositories(names_list, details):
    details_list = []
    for i in range(len(details)):
        details_list.append(details[i])
    zip_iteraor = zip(names_list, details_list)
    return dict(zip_iteraor)


if __name__ == '__main__':
    url_parameter = 'https://api.github.com/users/SimonDuperray/repos'
    headers_parameter = {
        "Authorization": ""
    }

    repositories = get_repositories(url_parameter, headers_parameter)
    repositories_names = get_repositories_names(repositories)
    repositories_dict = get_dict_repositories(repositories_names, repositories)
    print(json.dumps(repositories_dict, indent=2))