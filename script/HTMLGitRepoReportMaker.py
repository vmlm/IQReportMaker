import jinja2
import locale
from GitReposDataMaker import GitReposDataMaker
from ReportMaker import ReportMaker
# import argparse

URL_LIST_FILENAME = 'url_list'
# REPOS_PATH = 'Y:/repos'
REPOS_PATH = 'C:/Users/vlara/Documents/repo_report/repos'
OUTPUT_PATH = '../output/reportoutput.html'


class HTMLGitRepoReportMaker(ReportMaker):

    def __init__(self):
        self.reportdatamaker = GitReposDataMaker()
        self.template_path = r'../templates'
        self.template_filename = 'report_template.html'
        self.report_name = 'Reporte de repositorios'

    def _make_report(self, source):
        jinja_env = jinja2.Environment(loader=jinja2.
                                       FileSystemLoader(self.template_path))
        report_renderer = jinja_env.get_template(self.template_filename)
        return report_renderer.render(**source).encode('utf-8')


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
    htmltxt = r.make_report(source)
    htmldest = open(OUTPUT_PATH, "wb")
    htmldest.write(htmltxt)
    htmldest.close()
