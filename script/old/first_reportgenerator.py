import jinja2
import re
import datetime
import subprocess
import os

REPOS_PATH = 'C:/Users/vlara/Documents/repo_report/repos'
OUTPUT_PATH = '..//output//reportoutput.html'
TEMPLATES_PATH = '..//templates'
TEMPLATE_USED = 'report_template.html'

def parse_report_source(sourcetext):
    title_finder = re.compile('[\*= ]')
    info_finder = re.compile('(?P<date>\S+).+,'
                             '(?P<author>.*),'
                             '<(?P<email>.*)>,[a-z0-9]*,*'
                             '(?P<name>[^, ]*)[ ,]*'
                             '(?P<repostate>.*)')
    repos = []
    num_repos = 0
    current_sect = {}
    for line in sourcetext.splitlines():
        if line:
            lead_char = line[0]
            if (lead_char == '*' or lead_char == '='):
                line = title_finder.sub('', line).strip().lower()
                if lead_char == '*':
                    num_repos += 1
#                   start new repo
                    current_repo = {}
                    current_authors = []
                    current_repo['num'] = num_repos
                    current_repo['name'] = line
                    current_repo['authors'] = current_authors
                    repos.append(current_repo)
                else:
                    if current_sect:
                        current_repo[current_sect['name']] = \
                            current_sect['content']
#                       start new section
                    if not line == 'lastmonthmessages':
                        current_sect = {
                            'name': line,
                            'content': []
                        }
            elif (lead_char != ' '):
                extracted = info_finder.match(line)
                if extracted is not None:
                    content = extracted.groupdict()
                    current_sect['content'].append(content)
#                   format date
                    content['date'] = datetime. \
                        datetime.strptime(content['date'],
                                          '%Y-%m-%d').strftime('%d/%m/%Y')
#                   add repo unmerged comment
                    if len(content['repostate']):
                        content['name'] += ' (' + content['repostate'] + ')'
#                   make list of authors
                    if not any(author['name'] == content['author']
                               for author in current_authors):
                        current_authors.append({
                            'name': content['author'],
                            'email': content['email']
                        })
    return repos


if __name__ == "__main__":
    jinja_env = jinja2.Environment(loader=jinja2.
                                   FileSystemLoader(TEMPLATES_PATH))
    sourcetext = subprocess.check_output(['bash', './parse_repo.sh'],
                                         cwd=INPUT_PATH, env=os.environ).decode('utf-8')

#    sourcetext = subprocess.check_output(['bash', '-c printenv'], ).decode('utf-8')
    repos_json = parse_report_source(sourcetext)
    report = jinja_env.get_template(TEMPLATE_USED)
    htmltxt = report.render(reportmonth="agosto",
                            reportyear="2017",
                            repos=repos_json)
    htmldest = open(OUTPUT_PATH, "w")
    htmldest.write(htmltxt)
    htmldest.close()