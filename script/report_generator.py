import jinja2
import git
import os
from datetime import datetime
import locale
import LogMaker
from LogMaker import BranchLogMaker, TagLogMaker, LastCommitsLogMaker
# import argparse

URL_LIST_FILENAME = 'url_list'
REPOS_PATH = 'Y:/repos'
# REPOS_PATH = 'C:/Users/vlara/Documents/repo_report/repos'
OUTPUT_PATH = '../output/reportoutput.html'
TEMPLATES_PATH = '../templates'
TEMPLATE_USED = 'report_template.html'


def get_messages_info(repo):
    return repo.git.shortlog('--since=last month',
                             '--all',
                             '--format=%h,%s').splitlines()


def is_repo(repo_path):
    return '.git' in os.listdir(repo_path)


def repo_is_empty(repo):
    return 'No commits' in repo.git.status()


def get_authors(repo_info):
    authors = []
    all_commits = repo_info['branches'] + repo_info['tags']
    authors = [{'name': x['author'], 'email': x['email']} for x in all_commits]
    authors = [dict(y) for y in set(tuple(x.items()) for x in authors)]
    return authors


def make_repos_json(repos_list, repos_path):
    repos = []
    repo_num = 1
    for repo_name in repos_list:
        current_repo_info = {}
        repo_path = os.path.join(repos_path, repo_name)
        print(repo_name)
        current_repo_info['name'] = repo_name
        current_repo_info['num'] = repo_num
        repo_num += 1
        if not (os.path.isdir(repo_path) and is_repo(repo_path)):
            current_repo_info['status'] = 'does not exist'
        else:
            repo = git.Repo(repo_path)
            if repo_is_empty(repo):
                current_repo_info['status'] = 'empty'
            else:
                current_repo_info['status'] = 'ok'
                current_repo_info['branches'] = \
                    LogMaker.make_log(repo, BranchLogMaker())
                current_repo_info['tags'] = \
                    LogMaker.make_log(repo, TagLogMaker())
                current_repo_info['lastcommits'] = \
                    LogMaker.make_log(repo, LastCommitsLogMaker())
                current_repo_info['messages'] = [process_subject(
                                                 x.replace('      ',
                                                           '&emsp;'), 58)
                                                 for x in
                                                 get_messages_info(repo)]
                current_repo_info['authors'] = get_authors(current_repo_info)
            repo.close()
        repos.append(current_repo_info)
    return repos


def get_repos_list(file_name, repos_path):
    f = open(os.path.join(repos_path, '..', file_name), 'r')
    repo_list = [x.rsplit('/', 1)[-1] for x in f.read().splitlines()]
    f.close()
    return repo_list


# def setup_parser():
#     parser = argparse.ArgumentParser(
#                 description='Genera reporte mensual de repositorios IQ')
#     parser.add_argument('mes', help='mes a reportar')
#     parser.add_argument('año', help='año')
#     return parser


def get_monthyear(dt):
    locale.setlocale(locale.LC_ALL, 'es-419')
    return tuple(dt.strftime('%B,%Y').split(','))


if __name__ == "__main__":
    jinja_env = jinja2.Environment(loader=jinja2.
                                   FileSystemLoader(TEMPLATES_PATH))
#   parser = setup_parser()
#   opts = parser.parse_args()
    repos_list = get_repos_list(URL_LIST_FILENAME, REPOS_PATH)
    repos_json = make_repos_json(repos_list, REPOS_PATH)
    report = jinja_env.get_template(TEMPLATE_USED)
    month, year = get_monthyear(datetime.today())
    htmltxt = report.render(reportmonth=month,
                            reportyear=year,
                            repos=repos_json)
    htmldest = open(OUTPUT_PATH, "wb")
    htmldest.write(htmltxt.encode('utf-8'))
    htmldest.close()
