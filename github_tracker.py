import numpy as np 
import requests
import json
import collections
import matplotlib.pyplot as plt
import operator

"""
    ||=======================================||
    ||     data         |  SCRAP  |  RESULT  ||
    ||=======================================||
    || nb repos         |   OK    |    OK    ||
    ||=======================================||
    || nb commits graph |   OK    |    //    ||
    ||=======================================||
    || % languages      |   OK    |    OK    ||
    ||=======================================||
    || owner            |   OK    |    OK    ||
    ||=======================================||
    || created_at       |   OK    |    OK    ||
    ||=======================================||
"""

class GithubTracker:
    def __init__(self, url, token, repositories):
        self.url = url
        self.token = token
        self.repositories = repositories

    # unique request
    def unique_request(self):
        response = requests.get(
            self.url,
            headers = {
                "Authorization": self.token
            }
        ).json()
        self.repositories = response
        return response

    def get_number(self):
        return len(self.repositories)

    def get_data_from_global_repos(self, global_repos):
        name_list, creation_list, language_list = [], [], []
        for item in global_repos:
            name_list.append(item['name'])
            creation_list.append(item['created_at'])
            language_list.append(item['language'])
        for m in range(len(language_list)):
            if language_list[m] == None:
                language_list[m] = "NaN"
            else:
                pass
        return name_list, creation_list, language_list

    def get_creation_date_hour(self, creation_list):
        return [item[0:10] for item in creation_list], [item[-9:-1] for item in creation_list]

    def create_messages_dates_commits(self, details_commits, name_list):
        messages_dates_commits = {}
        for l in range(len(details_commits)):
            messages_commits_list, dates_commits_list = [], []
            for k in range(len(details_commits[list(details_commits.keys())[l]])):
                try:
                    messages_commits_list.append(details_commits[list(details_commits.keys())[l]][k]['commit']['message'])
                    dates_commits_list.append(details_commits[list(details_commits.keys())[l]][k]['commit']['committer']['date'][0:10])
                except KeyError as error:
                    print("KeyError: " + str(error))
            little_dict = {
                'number_commits': len(messages_commits_list),
                'messages': messages_commits_list,
                'dates': dates_commits_list
            }
            messages_dates_commits[name_list[l]] = little_dict
            little_dict = {}
        with open('database/messages_dates_commits.json','w') as outfile:
            json.dump(messages_dates_commits, outfile, indent=4)
        return messages_dates_commits

    def get_details_repos(self, name_list):
        details_repos = {}
        for i in range(len(name_list)):
            current_response = requests.get(
                f'https://api.github.com/repos/SimonDuperray/{name_list[i]}/commits',
                headers = {
                    "Authorization": self.token
                }
            ).json()
            details_repos[name_list[i]] = current_response
        return details_repos

    def donut_pie(self, language_list):
        sorted_data = dict(sorted(collections.Counter(language_list).items(), key=operator.itemgetter(1), reverse=True))
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

    def histogram(self, first, second, third, title):
        fig, axs = plt.subplots(2, 2, sharey = True, tight_layout = True)
        axs[0][0].hist(first)
        axs[0][1].hist(second)
        axs[1][0].hist(third)
        plt.show()

    def stats_creation_date(self, creation, language):
        years_list, months_list, days_list = [], [], []
        for i in range(len(creation)):
            current_splitted_list = creation[i].split('-')
            years_list.append(current_splitted_list[0])
            months_list.append(current_splitted_list[1])
            days_list.append(current_splitted_list[2][0:2])
        years_list.sort()
        months_list.sort()
        days_list.sort()
        counted_years = collections.Counter(years_list)
        counted_months = collections.Counter(months_list)
        counted_days = collections.Counter(days_list)
        self.histogram(first=years_list, second=months_list, third=days_list, title="Creation Date Stats")

if __name__ == '__main__':

    TOKEN = ""
    URL = ""

    tracker = GithubTracker(url=URL, token=TOKEN, repositories=None)
    
    repositories = tracker.unique_request()

    if next(iter(repositories)) == 'message':
        raise Exception('API rate limit exceeded !')

    try:
        name_list, creation_list, language_list = tracker.get_data_from_global_repos(repositories)
    except KeyError as error:
        print("KeyError (get_data_from_global_repos) -> " + str(error))

    repositories_number = tracker.get_number()
    if repositories_number <= 0:
        raise Exception("repositories list empty")

    owner = repositories[0]['owner']

    creation_date_list, creation_hour_list = tracker.get_creation_date_hour(creation_list = creation_list)

    details_repos = tracker.get_details_repos(name_list = name_list)

    messages_dates_commits = tracker.create_messages_dates_commits(details_commits = details_repos, name_list = name_list)

    # Get Results
    print("owner: "+str(owner['login']))
    print("number of repos: "+str(repositories_number))
    tracker.donut_pie(language_list = language_list)
    tracker.stats_creation_date(creation=creation_list, language=language_list)
