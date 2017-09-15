from abc import ABC, abstractmethod
from datetime import datetime
import re


class LogMaker(ABC):

    @abstractmethod
    def make_log(self, repo, logmaker):
        return NotImplemented

    def process_date(date_string,
                     input_format='%Y-%m-%d %H:%M:%S %z',
                     output_format='%d/%m/%Y'):
        return datetime.strptime(date_string,
                                 input_format
                                 ).strftime(output_format)

    def process_subject(subject_string, max_len=50):
        subject_string = subject_string\
            if len(subject_string) < max_len\
            else subject_string[:max_len - 1].strip() + '...'
        return subject_string


class CommitLogMaker(LogMaker):

    sorts = True
    sorting_opts = {
        'key': lambda k: k['date'],
        'reverse': True
    }
    info_finder = re.compile('(?P<date>[^,]*),'
                             '(?P<author>[^,]*),'
                             '<(?P<email>[^,]*)>,'
                             '(?P<hash>[a-z0-9]*),'
                             '(?P<subject>.*)')

    @abstractmethod
    def get_items(self, repo):
        return NotImplemented

    @abstractmethod
    def get_info(self, repo, item):
        return NotImplemented

    def process_info(self, extracted, item):
        content = extracted.groupdict()
        content['name'] = item
        content['date'] = self.process_date(content['date'])
        content['hash'] = content['hash'][:6]
        return self.additional_processing(content)

    def additional_processing(content):
        return content

    def make_log(self, repo, logmaker):
        items = []
        for item in logmaker.get_items(repo):
            extracted = self.get_info(repo, item)
            if extracted is not None:
                items.append(self.process_info(extracted, item))
        if items and self.sorts:
            items.sort(**self.sorting_opts)
        return items


class TagLogMaker(CommitLogMaker):

    def get_items(self, repo):
        return [x.name for x in repo.tags]

    def get_info(self, repo, item):
        commit_info = repo.git.log('-n1',
                                   '--format=%ai,%an,<%ae>,%H,%s',
                                   item)
        return self.info_finder.match(commit_info)


class BranchLogMaker(CommitLogMaker):

    def get_items(self, repo):
        return [x.name for x in repo.remotes.origin.refs
                if 'HEAD' not in x.name]

    def get_info(self, repo, item):
        commit_info = repo.git.show('--format=%ci,%cn,<%ce>,%H,%s',
                                    item).splitlines()[0]
        return self.info_finder.match(commit_info)


class LastCommitsLogMaker(CommitLogMaker):

    def get_items(self, repo):
        shortlog_out = repo.git.shortlog('-sne', '--all').splitlines()
        email_finder = re.compile('(<.*>)')
        return map(email_finder.search, shortlog_out)

    def get_info(self, repo, item):
        author_email = item.group(0)
        commit_hash = repo.git.log('-n1',
                                   '--all',
                                   '--committer={}'.format(author_email)
                                   ).splitlines()[0].split()[1]
        commit_info = repo.git.show('--format=%ci,%cn,<%ce>,%H,%s',
                                    commit_hash).splitlines()[0]
        return self.info_finder.match(commit_info)

    def additional_processing(self, content):
        content['subject'] = self.process_subject(content['subject'],
                                                  max_len=45)
        return content
