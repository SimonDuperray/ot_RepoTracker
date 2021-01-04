    messages_commit_list, dates_commit_list = [], []
    commits_and_dates_dict = {}
    for k in range(len(details_repos_dict_loaded[list(details_repos_dict_loaded.keys())[1]])):
        messages_commit_list.append(details_repos_dict_loaded[list(details_repos_dict_loaded.keys())[1]][k]['commit']['message'])
        dates_commit_list.append(details_repos_dict_loaded[list(details_repos_dict_loaded.keys())[1]][k]['commit']['committer']['date'][0:10])
    # print("messages_commit_list: "+str(messages_commit_list)+"\ndates_commit_list: "+str(dates_commit_list))
    little_dict = {
        'messages': messages_commit_list,
        'dates': dates_commit_list
    }
    commits_and_dates_dict[name_list[1]] = little_dict

    print(json.dumps(commits_and_dates_dict, indent=2))