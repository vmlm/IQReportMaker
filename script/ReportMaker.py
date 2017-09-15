from abc import ABC, abstractmethod


class ReportMaker(ABC):
    reportdatamaker = None
    report_name = 'undefined'

    @abstractmethod
    def _make_report(self, source):
        return NotImplemented

    def make_report(self, source):
        return self._make_report(self.reportdatamaker.
                                 make_data(source,
                                           self.report_name))
