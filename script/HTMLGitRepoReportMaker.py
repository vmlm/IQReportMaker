import locale
import os
from GitReposReportDataMaker import GitReposReportDataMaker
from HTMLReportMaker import HTMLReportMaker
# import argparse

URL_LIST_FILENAME = 'url_list'
# Test values
# REPOS_PATH = 'C:/Users/vlara/Documents/repo_report/repos'
# OUTPUT_PATH = '../output/'
REPOS_PATH = 'Y:/repos'
OUTPUT_PATH = 'Y:/reportes'


class HTMLGitRepoReportMaker(HTMLReportMaker):

    def __init__(self):
        self.reportdatamaker = GitReposReportDataMaker()
        self.template_path = r'../templates'
        self.template_filename = 'report_template.html'
        self.report_name = 'Reporte de repositorios'


# def setup_parser():
#     parser = argparse.ArgumentParser(
#                 description='Genera reporte mensual de repositorios IQ')
#     parser.add_argument('mes', help='mes a reportar')
#     parser.add_argument('año', help='año')
#     return parser

if __name__ == "__main__":
    url_file = 'url_list'
    source = {
        'path': REPOS_PATH,
        'file_name': URL_LIST_FILENAME
    }
#   parser = setup_parser()
#   opts = parser.parse_args()
    locale.setlocale(locale.LC_ALL, 'esp_esp')
    r = HTMLGitRepoReportMaker()
    report_data = r.make_data(source)
    for repo in report_data['repos']:
        file_name =\
            report_data['year'] + '-' +\
            report_data['month'] + '_' +\
            repo['name'] + '.html'
        output_path = os.path.join(OUTPUT_PATH, file_name)
        htmltxt = r.make_report(report_name=report_data['report_name'],
                                month=report_data['month'],
                                year=report_data['year'],
                                repo=repo)
        htmldest = open(output_path, "wb")
        htmldest.write(htmltxt)
        htmldest.close()
