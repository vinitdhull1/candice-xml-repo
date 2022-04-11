from .base import Model
from ..__commons__ import LOGGER_NAME
import logging
from nltk.tokenize import word_tokenize
logger = logging.getLogger(LOGGER_NAME)
from ..__paths__ import PATH_TO_RESOURCES
from ..__parameters__ import word_tokenizer,qoutes_tokenizer, single_qoutes_tokenizer
import pandas as pd
from .spelling_us_uk import US_UK
import re
import nltk
nltk.download('punkt')


class Quotation(Model):
    """
    --> Finds prefixes, deletes hyphens, and joins such words.
    -->
    """

    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'quotation'
        self._type = 'punctuation'

    def _add_quotes(self, doc):

        us_uk = US_UK(sent_list=self._sent_list, doc_name=self._doc_name)
        us_uk_type = us_uk._find_majority()
        str_doc = str(doc)
        objs = []
        data = list(enumerate(single_qoutes_tokenizer.span_tokenize(str(doc))))
        double_data = list(enumerate(qoutes_tokenizer.span_tokenize(str(doc))))
        all_data_span = [item.get('span') for idx, item in data if item.get('bracket_content')]
        all_double_data_span = [item.get('span') for idx, item in double_data if item.get('bracket_content')]
        data_span = [i for i in all_data_span for j in all_double_data_span if i[0] in range(j[0],j[1]) and i[1] in range(j[0],j[1])]
        double_data_span = [i for i in all_double_data_span for j in all_data_span if i[0] in range(j[0],j[1]) and i[1] in range(j[0],j[1])]
        if us_uk_type == 'uk':
            for idx, word in enumerate(doc):
                if word.text in ['’']:
                    if doc[idx-1].text in ['.', ',']:
                        objs.append({'token':"{}{}".format( doc[idx-1].text,word.text), 'start':doc[idx-1].idx, 
                            'stop':word.idx+len(word.text), 'change':"{}{}".format(word.text,doc[idx-1].text)})
                        if  doc[idx-1].text in [';', ':']:
                            objs.append({'token':"{}{}".format(doc[idx-1].text, word.text), 'start':doc[idx-1].idx,
                            'stop': word.idx+len(word.text), 'change':"{}{}".format(word.text, doc[idx-1].text)})


            for idx, item in double_data:
                if item.get('span') not in double_data_span:
                    if item.get('bracket_content'):
                        words = word_tokenize(item.get('text'))
                        if idx < len(double_data):
                            if words[-2] in ['.', ',',';',':']:
                                objs.append({'token': words[0], 'start': item.get('span')[0], 'stop': item.get('span')[0]+len(words[0]), 'change': '‘'})
                                objs.append({'token':"{}{}".format(words[-2],words[-1]),'start':item.get('span')[1]-(len(words[-2])+len(words[-1])+1),
                                    'stop': item.get('span')[1],'change': "’{}".format(words[-2]) })
                            else:
                                objs.append({'token': words[0],'start': item.get('span')[0], 'stop': item.get('span')[0]+len(words[0]), 'change': '‘'})
                                objs.append({'token': words[-1], 'start': item.get('span')[1] - len(words[-1]),
                                    'stop': item.get('span')[1],'change': '’'})
                        for in_quote in single_qoutes_tokenizer.span_tokenize(item.get('text')):
                            if in_quote.get('bracket_content'):
                                words = word_tokenize(in_quote.get('text'))
                                objs.append({'token': words[0],'start': item.get('span')[0]+in_quote.get('span')[0], 
                                    'stop':  item.get('span')[0]+in_quote.get('span')[0]+len(words[0]), 'change': '“'})
                                objs.append({'token': words[-1], 'start':  item.get('span')[0]+in_quote.get('span')[1] - len(words[-1]),
                                    'stop':  item.get('span')[0]+in_quote.get('span')[1],'change': '”'})

        if us_uk_type == 'us':
            for idx, word in enumerate(doc):
                if word.text in ['”']:
                    if idx+1 < len(doc) and doc[idx+1].text in ['.', ',']:
                        objs.append({'token':"{}{}".format(word.text, doc[idx+1].text), 'start':word.idx, 
                            'stop':doc[idx+1].idx+len(doc[idx+1].text), 'change':"{}{}".format( doc[idx+1].text,word.text)})
                        if  doc[idx-1].text in [';',":"]:
                            objs.append({'token':"{}{}".format(doc[idx-1].text, word.text), 'start':doc[idx-1].idx,
                            'stop': word.idx+len(word.text), 'change':"{}{}".format(word.text, doc[idx-1].text)})


            for idx, item in data:
                if item.get('span') not in double_data_span:
                    if item.get('bracket_content'):
                        words = word_tokenize(item.get('text'))
                        if idx+1 < len(data):
                            next_word = word_tokenize( data[idx+1][1].get('text'))
                            if len(next_word) > 0 and next_word[0] in ['.', ',']:
                                objs.append({'token': words[0], 'start': item.get('span')[0], 'stop': item.get('span')[0]+len(words[0]), 'change': '“'})
                                objs.append({'token':"{}{}".format(words[-1],next_word[0]),'start': item.get('span')[1]-len(words[-1]),
                                    'stop': item.get('span')[1]+ len(next_word[0])+1,'change': "{}”".format(next_word[0]) })
                        
                            elif words[-2] in [";", ':']:
                                objs.append({
                                    'token': words[0], 'start': item.get('span')[0], 'stop': item.get('span')[0]+len(words[0]),'change': '“'})
                                objs.append({
                                    'token':"{}{}".format(words[-2],words[-1]), 'start': item.get('span')[1]-(len(words[-2])+len(words[-1])+1),
                                    'stop': item.get('span')[1],'change': "”{}".format(words[-2])})

                            else:
                                objs.append({'token': words[0],'start': item.get('span')[0], 'stop': item.get('span')[0]+len(words[0]), 'change': '“'})
                                objs.append({'token': words[-1], 'start': item.get('span')[1] - len(words[-1]),
                                'stop': item.get('span')[1],'change': '”'})
                        for in_quote in qoutes_tokenizer.span_tokenize(item.get('text')):
                            if in_quote.get('bracket_content'):
                                words = word_tokenize(in_quote.get('text'))
                                objs.append({'token': words[0],'start': item.get('span')[0]+in_quote.get('span')[0], 
                                    'stop':  item.get('span')[0]+in_quote.get('span')[0]+len(words[0]), 'change': '‘'})
                                objs.append({'token': words[-1], 'start':  item.get('span')[0]+in_quote.get('span')[1] - len(words[-1]),
                                'stop':  item.get('span')[0]+in_quote.get('span')[1],'change': '’'})

        return objs

    def transform(self, add_all, del_all, com_all):
        self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []
        docs = self._get_spacy_docs()

        for idx, doc in enumerate(docs):
            obj = self._add_quotes(doc)
            _temp_add, _temp_del, _temp_com = [], [], []
            for item in obj:
                if item['change'] != item['token']:
                    start, stop = self._map_span((item['start'], item['stop']), self._span_maps[idx])
                    add_map = self._return_add_map(pos=stop, token=item['change'])
                    del_map = self._return_del_map(start=start, stop=stop, token=self._sent_list[idx][start:stop])
                    if del_map['stop'] - del_map["start"] <= 3:
                        if self.check_existent_map(add_map, add_all[idx]) and self.check_existent_map(del_map, del_all[idx]):
                            continue
                        self._num_errors += 1
                        _temp_del.append(del_map)
                        _temp_add.append(add_map)
                    else:
                        del_map['stop'] = del_map['start']+1
                        del_map['token'] = del_map['token'][0]
                        add_map['position'] = del_map['stop']
                        add_map['token'] = add_map['token'][-1]
                        if add_map['token'] !=  del_map['token']:
                            if self.check_existent_map(add_map, add_all[idx]) and self.check_existent_map(del_map, del_all[idx]):
                                continue
                            self._num_errors += 1
                            _temp_del.append(del_map)
                            _temp_add.append(add_map)


            add_.append(_temp_add)
            del_.append(_temp_del)
            com_.append([])

        return add_, del_, com_
