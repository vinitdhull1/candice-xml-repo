from .base import Model
from ..__commons__ import LOGGER_NAME
import logging

logger = logging.getLogger(LOGGER_NAME)
from ..__paths__ import PATH_TO_RESOURCES
from ..__parameters__ import word_tokenizer
import pandas as pd


def read_hyphen_list():
    """
    --> Read prefix_list csv
    :return
    """
    df = pd.read_csv(PATH_TO_RESOURCES.joinpath('hyphen-ins.csv').as_posix())
    insert = df['insert'].apply(lambda x: x.lower()).values.tolist()
    delete = df['delete'].apply(lambda x: x.lower()).values.tolist()
    return insert, delete


insert, delete = read_hyphen_list()

class Hyphen_Add(Model):
    """
    --> Add hyphens
    -->
    """

    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'hyphen_add'
        self._type = 'punctuation'

    @staticmethod
    def _add_hyphen(doc):
        objs = []
        for idx, word in enumerate(doc):

            if word.text in delete:
                index = delete.index(word.text)

                objs.append({
                    'token': word.text,
                    'start': word.idx,
                    'stop': word.idx + len(word.text),
                    'change': insert[index]})
        return objs

    def transform(self, add_all, del_all, com_all):
        self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []
        docs = self._get_spacy_docs()

        for idx, doc in enumerate(docs):
            obj = self._add_hyphen(doc)
            _temp_add, _temp_del, _temp_com = [], [], []
            for item in obj:

                start, stop = self._map_span((item['start'], item['stop']), self._span_maps[idx])
                del_map = self._return_del_map(start=start, stop=stop, token=self._sent_list[idx][start:stop])
                add_map = self._return_add_map(pos=stop, token=item['change'])
                if self.check_existent_map(add_map, add_all[idx]) and self.check_existent_map(del_map, del_all[idx]):
                    continue
                self._num_errors += 1
                _temp_del.append(del_map)
                _temp_add.append(add_map)
            add_.append(_temp_add)
            del_.append(_temp_del)
            com_.append([])

        return add_, del_, com_
