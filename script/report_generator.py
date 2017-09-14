import jinja2
import re
import git
import os
from datetime import datetime
import locale
# import argparse

URL_LIST_FILENAME = 'url_list'
REPOS_PATH = 'Y:/repos'
# REPOS_PATH = 'C:/Users/vlara/Documents/repo_report/repos'
OUTPUT_PATH = '../output/reportoutput.html'
TEMPLATES_PATH = '../templates'
TEMPLATE_USED = 'report_template.html'


def process_gitdate(date_string):
    return datetime.strptime(date_string,
                             '%Y-%m-%d %H:%M:%S %z'
                             ).strftime('%d/%m/%Y')


def process_subject(subject_string, max_len):
    subject_string = subject_string\
        if len(subject_string) < max_len\
        else subject_string[:max_len - 1].strip() + '...'
    return subject_string


def get_branch_info(repo):
    branches = []
    info_finder = re.compile('(?P<date>[^,]*),'
                             '(?P<author>[^,]*),'
                             '<(?P<email>[^,]*)>,'
                             '(?P<hash>[a-z0-9]*),'
                             '(?P<subject>.*)')
    branch_names = [x.name for x in repo.remotes.origin.refs
                    if 'HEAD' not in x.name]
    for branch_name in branch_names:
        commit_info = repo.git.show('--format=%ci,%cn,<%ce>,%H,%s',
                                    branch_name).splitlines()[0]
        extracted = info_finder.match(commit_info)
        if extracted is not None:
            content = extracted.groupdict()
            content['name'] = branch_name
            content['date'] = process_gitdate(content['date'])
            content['hash'] = content['hash'][:6]
            if branch_name not in repo.git.branch('-a', '--no-merged'):
                content['merged'] = False
            else:
                content['merged'] = True
            branches.append(content)
    if branches:
        branches.sort(key=lambda k: k['date'], reverse=True)
    return branches


def get_tag_info(repo):
    tags = []
    info_finder = re.compile('(?P<date>[^,]*),'
                             '(?P<author>[^,]*),'
                             '<(?P<email>[^,]*)>,'
                             '(?P<hash>[a-z0-9]*),'
                             '(?P<subject>.*)')
#   iterate over all non head lines
    for tag_name in [x.name for x in repo.tags]:
        commit_info = repo.git.log('-n1',
                                   '--format=%ai,%an,<%ae>,%H,%s',
                                   tag_name)
        extracted = info_finder.match(commit_info)
        if extracted is not None:
            content = extracted.groupdict()
            content['name'] = tag_name
            content['date'] = process_gitdate(content['date'])
            content['hash'] = content['hash'][:6]
            tags.append(content)
    if tags:
        tags.sort(key=lambda k: k['date'], reverse=True)
    return tags


def get_commit_log(repo):
    commits = []
    itemlist_getter = (repo.git.shortlog, ('-sne', '--all'), splitlines=True)
    item_finder = (pattern='(<.*>)', params="", method='search')
    info_finder = (pattern='(<.*>)', params="", method='match')
    



def get_lastcommit_info(repo):
    last_commits = []
    shortlog_out = repo.git.shortlog('-sne', '--all').splitlines()
    email_finder = re.compile('(<.*>)')
    info_finder = re.compile('(?P<date>[^,]*),'
                             '(?P<author>[^,]*),'
                             '<(?P<email>[^,]*)>,'
                             '(?P<hash>[a-z0-9]*),'
                             '(?P<subject>.*)')
#   iterate over all non head lines
    for match in map(email_finder.search, shortlog_out):
        author_email = match.group(0)
        commit_hash = repo.git.log('-n1',
                                   '--all',
                                   '--committer={}'.format(author_email)
                                   ).splitlines()[0].split()[1]
        commit_info = repo.git.show('--format=%ci,%cn,<%ce>,%H,%s',
                                    commit_hash).splitlines()[0]
        extracted = info_finder.match(commit_info)
        if extracted is not None:
            content = extracted.groupdict()
            content['date'] = process_gitdate(content['date'])
            content['subject'] = process_subject(content['subject'],
                                                 max_len=45)
            last_commits.append(content)
    if last_commits:
        last_commits.sort(key=lambda k: k['date'], reverse=True)
    return last_commits


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


def make_json(repos_list, repos_path):
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
                current_repo_info['branches'] = get_branch_info(repo)
                current_repo_info['tags'] = get_tag_info(repo)
                current_repo_info['lastcommits'] = get_lastcommit_info(repo)
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
    repos_json = make_json(repos_list, REPOS_PATH)
    report = jinja_env.get_template(TEMPLATE_USED)
    month, year = get_monthyear(datetime.today())
    htmltxt = report.render(reportmonth=month,
                            reportyear=year,
                            repos=repos_json)
    htmldest = open(OUTPUT_PATH, "wb")
    htmldest.write(htmltxt.encode('utf-8'))
    htmldest.close()
