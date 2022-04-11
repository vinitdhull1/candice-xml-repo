from .base import Model
from ..__paths__ import PATH_TO_RESOURCES
from ..__parameters__ import word_tokenizer
from ..__commons__ import LOGGER_NAME
import logging

logger = logging.getLogger(LOGGER_NAME)

with open(PATH_TO_RESOURCES.joinpath('comma_introductory_phrases'), 'r', encoding='utf-8') as f:
    comma_list = f.readlines()


class Comma(Model):
    """
    --> correct wrong usage of comma
    TO DO
        1. get examples of introductory phrases from data
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'comma'
        self._type = 'punctuation'

    @staticmethod
    def __suggest_comma(text):
        tokens = word_tokenizer.tokenize(text)
        spans = list(word_tokenizer.span_tokenize(text))

        if tokens and tokens[0] in comma_list:
            if len(tokens) > 2:
                if tokens[1] != ',':
                    return [{
                        'token': tokens[0],
                        'start': spans[0][0],
                        'stop': spans[0][1]
                    }]

    def transform(self, add_all, del_all, com_all):
        self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []

        for idx, text in enumerate(self._sent_list):
            obj = Comma.__suggest_comma(text)
            _temp_add, _temp_del, _temp_com = [], [], []
            if not obj:
                add_.append([])
                del_.append([])
                com_.append([])
            else:
                for item in obj:
                    add_map = self._return_add_map(pos=item['stop'], token=',')
                    if self.check_existent_map(add_map, add_all[idx]):
                        continue
                    self._num_errors += 1
                    _temp_add.append(add_map)
                add_.append(_temp_add)
                del_.append([])
                com_.append([])

        return add_, del_, com_
