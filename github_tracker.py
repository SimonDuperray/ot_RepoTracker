import pandas as pd
import numpy as np 
import requests
from bs4 import BeautifulSoup
import json
from IPython.display import display
import collections
import matplotlib.pyplot as plt
import operator

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

def is_included(elem_list, found_to_list):
    for item in elem_list:
        for isin in found_to_list:
            if item in isin:
                return True
                break

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
    # in language_list, replace None by NaN
    for m in range(len(language_list)):
        if language_list[m] == None:
            language_list[m] = "NaN"
        else:
            pass
    
    return name_list, id_list, creation_list, update_list, push_list, language_list

def get_date_and_hour(creation):
    return [index[0:10] for index in creation], [index[-9:-1] for index in creation]

def create_databases():
    # stock repo request in json file
    global_repo_json = 'database/global_repos.json'
    with open(global_repo_json, "w") as global_outfile:
        json.dump(repositories, global_outfile, indent=4)

    # stock details repos
    details_repos_dict = {}
    for i in range(len(name_list)):
        current_request = requests.get(
            f"https://api.github.com/repos/SimonDuperray/{name_list[i]}/commits",
            headers=headers_parameter
        )
        current_response = current_request.json()
        details_repos_dict[name_list[i]] = current_response
    details_repo_json = 'database/details_repos.json'
    with open(details_repo_json, "w") as details_outfile:
        json.dump(details_repos_dict, details_outfile, indent=4)

def create_messages_dates_commits(details_repos_dict_loaded, name_list):
    commits_and_dates_dict = {}
    # for each project in name_list
    for l in range(len(details_repos_dict_loaded)):
        messages_commit_list, dates_commit_list = [], []
        # for all messages and dates in each repository
        for k in range(len(details_repos_dict_loaded[list(details_repos_dict_loaded.keys())[l]])):
            try:
                messages_commit_list.append(details_repos_dict_loaded[list(details_repos_dict_loaded.keys())[l]][k]['commit']['message'])
                dates_commit_list.append(details_repos_dict_loaded[list(details_repos_dict_loaded.keys())[l]][k]['commit']['committer']['date'][0:10])
            except KeyError as error:
                print('KeyError: '+str(error))
        little_dict = {
            'number_commits': len(messages_commit_list),
            'messages': messages_commit_list,
            'dates': dates_commit_list,
        }
        commits_and_dates_dict[name_list[l]] = little_dict
        little_dict={}

    with open('database/messages_dates_commits.json','w') as outfile:
        json.dump(commits_and_dates_dict, outfile, indent=4)

    return commits_and_dates_dict

def check_required_data(name, id, language, creation_date, creation_hour, owner, push_date, push_hour):
    print("\n***** check_required_data *****\n")
    print("name: "+str(name)+"\n")
    print("id: "+str(id)+"\n")
    print("language: "+str(language)+"\n")
    print("creation_date: "+str(creation_date)+"\n")
    print("creation_hour: "+str(creation_hour)+"\n")
    print("owner: "+str(owner)+"\n")
    print("push_date: "+str(push_date)+"\n")
    print("push_hour: "+str(push_hour)+"\n")
    print("***** END CHECKING *****\n")

def get_donut_pie(data_list):
    sorted_data = dict(sorted(collections.Counter(data_list).items(), key=operator.itemgetter(1), reverse=True))
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(sorted_data.values(), wedgeprops=dict(width=0.5), startangle=-40)
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
            bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(list(sorted_data.keys())[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)
    current_title = "No Title"
    ax.set_title(current_title)
    plt.show()

def get_languages_proportion_txt(language_list, repositories_number):
    pourcentages_list = []
    sorted_counter = dict(sorted(collections.Counter(language_list).items(), key=operator.itemgetter(1), reverse=True))
    for j in range(len(list(sorted_counter.values()))):
        pourcentages_list.append(round(100*(int(list(sorted_counter.values())[j]))/repositories_number, 2))
    zip_iterator = zip(list(sorted_counter.keys()), pourcentages_list)
    final_pourcentage_languages = dict(zip_iterator)
    cls_indexes = [i for i in range(1, len(language_list)+1)]
    to_return = '''\n'''
    for o in range(len(list(final_pourcentage_languages.values()))):
        to_return += "{cpt}. {language} -> {pourcent}%".format(cpt=o, language=list(final_pourcentage_languages.keys())[o], pourcent=list(final_pourcentage_languages.values())[o])+"\n"
    return to_return

if __name__ == '__main__':
    url_parameter = 'https://api.github.com/users/SimonDuperray/repos'
    headers_parameter = {
        "Authorization": ""
    }

    # get all repositories of owner
    repositories = get_repositories(url_parameter, headers_parameter)

    # get lists of precise data from repositories list
    try:
        name_list, id_list, creation_list, update_list, push_list, language_list = get_required_data(repositories)
    except KeyError as error:
        # print("KeyError (get_required_data()): "+str(error))
        print("\n")

    # load details repositories from json file
    with open('database/details_repos.json') as reader:
        details_repos_dict_loaded = json.load(reader)

    # number of repositories
    repositories_number = len(repositories)
    if repositories_number<=0:
        raise Exception("repositories list empty")
                            
    # get owner infos
    owner = repositories[0]['owner']

    # get date and hour from creation_list
    creation_date_list, creation_hour_list = get_date_and_hour(creation_list)
    push_date_list, push_hour_list = get_date_and_hour(push_list)

    # create messages_dates_commits dict
    messages_dates_commits = create_messages_dates_commits(details_repos_dict_loaded, name_list)

    # result: number
    print(f"********************************************\nI detected {repositories_number} repositories.\n********************************************")

    # result: languages proportion graph
    # get_donut_pie(language_list)
    # result: languages proportion text
    print("This is your used languages distribution:\n"+str(get_languages_proportion_txt(language_list, repositories_number))+"********************************************")