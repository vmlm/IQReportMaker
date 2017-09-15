from abc import ABC, abstractmethod
from datetime import datetime


class DataProcessor(ABC):
    name = 'undefined'

    @abstractmethod
    def make_data(self, source):
        return NotImplemented

    def process_date(self, date_string,
                     input_format='%Y-%m-%d %H:%M:%S %z',
                     output_format='%d/%m/%Y'):
        return datetime.strptime(date_string,
                                 input_format
                                 ).strftime(output_format)

    def process_subject(self, subject_string, max_len=50):
        subject_string = subject_string\
            if len(subject_string) < max_len\
            else subject_string[:max_len - 1].strip() + '...'
        return subject_string
