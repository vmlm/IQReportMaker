
from abc import ABC, abstractmethod


class ReportDataMaker(ABC):
    info_processors = []
    info_aggregators = []

    def make_data(self, source, report_name):
        json_out = {
            'report_name': report_name
        }
        self._make_data(source, json_out)
        return json_out

    @abstractmethod
    def _make_data(source, json_out):
        return NotImplemented

    def populate_json(self, json_out, source):
        for processor in self.info_getters:
            json_out[processor.name] = processor.make_data(source)
        for aggregator in self.info_aggregators:
            json_out[aggregator.name] = aggregator.make_data(json_out)
