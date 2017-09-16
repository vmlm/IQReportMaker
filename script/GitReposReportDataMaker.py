from ReportDataMaker import ReportDataMaker
from GitDataProcessors import *
from datetime import datetime
import os
import git


class GitReposDataMaker(ReportDataMaker):

    def __init__(self):
        self.info_getters = [
            BranchInfoProcessor(),
            TagInfoProcessor(),
            LastCommitsInfoProcessor(),
            GitMessagesProcessor(),
        ]
        self.info_aggregators = [
            AuthorsAggregator()
        ]

    def is_repo(self, repo_path):
        return '.git' in os.listdir(repo_path)

    def repo_is_empty(self, repo):
        return 'No commits' in repo.git.status()

    def get_monthyear(self, dt):
        return tuple(dt.strftime('%B,%Y').split(','))

    def get_repos_list(self, file_path):
        f = open(file_path, 'r')
        repo_list = [x.rsplit('/', 1)[-1] for x in f.read().splitlines()]
        f.close()
        return repo_list

    def _make_data(self, source, json_out):
        repos_path = source['path']
        repos_list = self.get_repos_list(os.path.join(
                                         repos_path,
                                         '..',
                                         source['file_name']))
        repos = []
        json_out['month'], json_out['year'] =\
            self.get_monthyear(datetime.today())
        repo_num = 1
        for repo_name in repos_list:
            current_repo_info = {}
            repo_path = os.path.join(repos_path, repo_name)
            print(repo_name)
            current_repo_info['name'] = repo_name
            current_repo_info['num'] = repo_num
            repo_num += 1
            if not (os.path.isdir(repo_path) and self.is_repo(repo_path)):
                current_repo_info['status'] = 'does not exist'
            else:
                repo = git.Repo(repo_path)
                if self.repo_is_empty(repo):
                    current_repo_info['status'] = 'empty'
                else:
                    current_repo_info['status'] = 'ok'
                    self.populate_json(current_repo_info, repo)
                repo.close()
            repos.append(current_repo_info)
        json_out['repos'] = repos
