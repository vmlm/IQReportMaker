from abc import ABC, abstractmethod


class ReportMaker(ABC):
    reportdatamaker = None
    report_name = 'undefined'

    @abstractmethod
    def _make_report(self, source):
        return NotImplemented

    def make_report(self, **data_obj):
        return self._make_report(data_obj)

    def make_data(self, source):
        return self.reportdatamaker.make_data(source, self.report_name)
