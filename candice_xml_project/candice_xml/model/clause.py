from .base import Model
import pandas as pd
from ..__paths__ import PATH_TO_RESOURCES
from ..__parameters__ import word_tokenizer
from ..__commons__ import LOGGER_NAME
import logging

logger = logging.getLogger(LOGGER_NAME)

clause_context_list = ['{} {}'.format(row['left'], row['right']) for _, row in
                       pd.read_csv(PATH_TO_RESOURCES.joinpath('clause.csv')).iterrows()]


class Clauses(Model):
    """
    # To Do
        1. explore context dep, pos
    """

    def __init__(self, *args, **kwargs):
        logger.debug('class :: {}, function :: {}'.format(self.__class__.__name__,
                                                          '__init__'))

        super().__init__(*args, **kwargs)
        self._name = 'clauses'
        self._type = 'grammar'

    @staticmethod
    def __get_suggestion(text):
        tokens = word_tokenizer.tokenize(text)
        span_tokens = list(word_tokenizer.span_tokenize(text))

        ret_obj = []
        for idx, token in enumerate(tokens):
            if token == 'which':
                if '{} {}'.format(tokens[idx - 1], tokens[idx + 1]) in clause_context_list:
                    ret_obj.append({'start': span_tokens[idx][0], 'stop': span_tokens[idx][1],
                                    'new': 'that', 'old': 'which'})
        return ret_obj

    def transform(self, add_all, del_all, com_all):
        self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        logger.debug('class :: {}, function :: {}'.format(self.__class__.__name__,
                                                          self.transform.__name__))

        add_, del_, com_ = [], [], []
        for idx, sent in enumerate(self._sent_list):
            obj = Clauses.__get_suggestion(sent)

            if not obj:
                add_.append([])
                del_.append([])
                com_.append([])
            else:
                temp_add, temp_del = [], []
                for item in obj:
                    add_map = self._return_add_map(pos=item['stop'], token=item['new'])
                    del_map = self._return_del_map(start=item['start'], stop=item['stop'],
                                                         token=item['old'])

                    if self.check_existent_map(add_map, add_all[idx]) and self.check_existent_map(del_map, del_all[idx]):
                        continue
                    self._num_errors += 1
                    temp_add.append(add_map)
                    temp_del.append(del_map)

                com_.append([])
                add_.append(temp_add)
                del_.append(temp_del)

        return add_, del_, com_
