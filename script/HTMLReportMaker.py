from ReportMaker import ReportMaker
import jinja2


class HTMLReportMaker(ReportMaker):
    template_path = 'undefined'
    template_filename = 'undefined'

    def _make_report(self, data_obj):
        jinja_env = jinja2.Environment(loader=jinja2.
                                       FileSystemLoader(self.template_path))
        report_renderer = jinja_env.get_template(self.template_filename)
        return report_renderer.render(**data_obj).encode('utf-8')
