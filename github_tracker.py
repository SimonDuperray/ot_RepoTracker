import pandas as pd
import numpy as np 
import requests
from bs4 import BeautifulSoup
import json
from IPython.display import display

"""
Infos to scrap:
    * % languages          | OK
    * nb repos             | OK
    * nb commits graph     | OK
    * name                 | OK
    * id                   | OK
    * owner                | OK
    * created_at           | OK
    * updated_at           | OK
    * pushed_at            | OK

    *********************************
    get messages and dates
        - {
            name_list[0]: {
                'messages': [...],
                'dates': [...]
            },
            name_list[1]: {
                'messages': [...],
                'dates': [...]
            },
            ..., 
            name_list[-1]: {
                'messages': [...],
                'dates': [...]
            }
        }
    *********************************
"""

base_url = "https://api.github.com"

def get_repositories(url, headers):
    return requests.get(url, headers=headers).json()

def get_required_data(repos_list):
    name_list, id_list, creation_list, update_list, push_list, language_list = [], [], [], [], [], []
    for item in repos_list:
        name_list.append(item['name'])
        id_list.append(item['id'])
        creation_list.append(item['created_at'])
        update_list.append(item['updated_at'])
        push_list.append(item['pushed_at'])
        language_list.append(item['language'])
    return name_list, id_list, creation_list, update_list, push_list, language_list

def get_date_and_hour(creation):
    return [index[0:10] for index in creation], [index[-9:-1] for index in creation]

if __name__ == '__main__':
    url_parameter = 'https://api.github.com/users/SimonDuperray/repos'
    headers_parameter = {
        "Authorization": ""
    }

    repositories = get_repositories(url_parameter, headers_parameter)

    name_list, id_list, creation_list, update_list, push_list, language_list = get_required_data(repositories)

    # stock repo request in json file
    # global_repo_json = 'database/global_repos.json'
    # with open(global_repo_json, "w") as global_outfile:
    #     json.dump(repositories, global_outfile, indent=4)

    # stock details repos
    # details_repos_dict = {}
    # for i in range(len(name_list)):
    #     current_request = requests.get(
    #         f"https://api.github.com/repos/SimonDuperray/{name_list[i]}/commits",
    #         headers=headers_parameter
    #     )
    #     current_response = current_request.json()
    #     details_repos_dict[name_list[i]] = current_response
    # details_repo_json = 'database/details_repos.json'
    # with open(details_repo_json, "w") as details_outfile:
    #     json.dump(details_repos_dict, details_outfile, indent=4)

    # get dict from json
    with open('database/details_repos.json') as reader:
        details_repos_dict_loaded = json.load(reader)

    # print(json.dumps(details_repos_dict_loaded, indent=2))

    # nb repos
    repositories_number = len(repositories)

    # owner
    owner = repositories[0]['owner']

    # get date and hour from creation_list
    creation_date_list, creation_hour_list = get_date_and_hour(creation_list)

    # ***************************************************************************************************************************************

    # for i in range(len(name_list)):
    #     messages_commits, dates_commits = [], []
    #     current_request = requests.get(
    #         f"https://api.github.com/repos/SimonDuperray/{name_list[i]}/commits",
    #         headers=headers_parameter
    #     )
    #     current_response = current_request.json()
    #     if i==1:
    #         # print(json.dumps(current_response[0], indent=2))
    #         print(str(current_response[0]['commit']['message'])+" "+str(current_response[0]['commit']['committer']['date']))
    #         break;
        
    # ***************************************************************************************************************************************
    
    commits_and_dates_dict = {}
    # for each project in name_list
    for l in range(len(details_repos_dict_loaded)):
        messages_commit_list, dates_commit_list = [], []
        # for all messages and dates in each repository
        for k in range(len(details_repos_dict_loaded[list(details_repos_dict_loaded.keys())[l]])):
            try:
                # print("current_index: "+str(list(details_repos_dict_loaded.keys())[l]))
                messages_commit_list.append(details_repos_dict_loaded[list(details_repos_dict_loaded.keys())[l]][k]['commit']['message'])
                dates_commit_list.append(details_repos_dict_loaded[list(details_repos_dict_loaded.keys())[l]][k]['commit']['committer']['date'][0:10])
            except KeyError:
                print('KeyError')
        # print(str(name_list[l])+": "+str(len(messages_commit_list))+": "+str(messages_commit_list)+"\n")
        little_dict = {
            'number_commits': len(messages_commit_list),
            'messages': messages_commit_list,
            'dates': dates_commit_list,
        }
        # print("NUMBER_COMMITS (little_dict)"+str(name_list[l])+": "+str(little_dict['number_commits']))
        commits_and_dates_dict[name_list[l]] = little_dict
        little_dict={}

    with open('database/messages_dates_commits.json','w') as outfile:
        json.dump(commits_and_dates_dict, outfile, indent=4)
        
    with open('database/messages_dates_commits.json') as mdc_reader:
        messages_dates_commits = json.load(mdc_reader)

    