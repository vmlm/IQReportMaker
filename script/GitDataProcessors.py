from DataProcessor import DataProcessor
from abc import abstractmethod
import re


class GitCommitInfoProcessor(DataProcessor):
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
    def get_items(self, source):
        return NotImplemented

    @abstractmethod
    def get_info(self, source, item):
        return NotImplemented

    def process_info(self, extracted, item):
        content = extracted.groupdict()
        content['name'] = item
        content['date'] = self.process_date(content['date'])
        content['hash'] = content['hash'][:6]
        return self.additional_processing(content)

    def additional_processing(self, content):
        return content

    def make_data(self, source):
        items = []
        for item in self.get_items(source):
            extracted = self.get_info(source, item)
            if extracted is not None:
                items.append(self.process_info(extracted, item))
        if items and self.sorts:
            items.sort(**self.sorting_opts)
        return items


class TagInfoProcessor(GitCommitInfoProcessor):

    def __init__(self):
        self.name = 'tags'

    def get_items(self, source):
        return [x.name for x in source.tags]

    def get_info(self, source, item):
        commit_info = source.git.log('-n1',
                                     '--format=%ai,%an,<%ae>,%H,%s',
                                     item)
        return self.info_finder.match(commit_info)


class BranchInfoProcessor(GitCommitInfoProcessor):

    def __init__(self):
        self.name = 'branches'

    def get_items(self, source):
        return [x.name for x in source.remotes.origin.refs
                if 'HEAD' not in x.name]

    def get_info(self, source, item):
        commit_info = source.git.show('--format=%ci,%cn,<%ce>,%H,%s',
                                      item).splitlines()[0]
        return self.info_finder.match(commit_info)


class LastCommitsInfoProcessor(GitCommitInfoProcessor):

    def __init__(self):
        self.name = 'lastcommits'

    def get_items(self, source):
        shortlog_out = source.git.shortlog('-sne', '--all').splitlines()
        email_finder = re.compile('(<.*>)')
        return map(email_finder.search, shortlog_out)

    def get_info(self, source, item):
        author_email = item.group(0)
        commit_hash = source.git.log('-n1',
                                     '--all',
                                     '--committer={}'.format(author_email)
                                     ).splitlines()[0].split()[1]
        commit_info = source.git.show('--format=%ci,%cn,<%ce>,%H,%s',
                                      commit_hash).splitlines()[0]
        return self.info_finder.match(commit_info)

    def additional_processing(self, content):
        content['subject'] = self.process_subject(content['subject'],
                                                  max_len=45)
        return content


class AuthorsAggregator(DataProcessor):

    def __init__(self):
        self.name = 'authors'

    def make_data(self, source):
        all_commits = source['branches'] + source['tags']
        authors = [{'name': x['author'], 'email': x['email']}
                   for x in all_commits]
        return [dict(y) for y in set(tuple(x.items()) for x in authors)]


class GitMessagesProcessor(DataProcessor):

    def __init__(self):
        self.name = 'messages'

    def make_data(self, source):
        messages_info = source.git.shortlog('--since=last month',
                                            '--all',
                                            '--format=%h,%s').splitlines()
        return [self.process_subject(x.replace('      ', ''), 80)
                for x in messages_info]
