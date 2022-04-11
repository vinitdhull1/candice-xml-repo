#-*- coding: utf-8 -*-

from .base import Model
from ..__commons__ import LOGGER_NAME
import logging

logger = logging.getLogger(LOGGER_NAME)
from ..__paths__ import PATH_TO_RESOURCES
import re

cross_references_list = {'fig':'Figure', 'figs':'Figures','figure':'Figure','Figures':'Figures','fig.':'Figure',
               'section':'Section','sec':'Section','sec.':'Section','sections':'Sections',
               'chapter':'Chapter','chap':'Chapter','chap.':'Chapter','chapters':'Chapters',
               'tables':'Tables','table':'Table','tab':'Table',
               'equation':'Equation','equations':'Equations','eq.':'Equation','eq':'Equation'}

    
class CapitalCorrections(Model):

    def __init__(self,
                *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'capitalisation'
        self._type = 'grammar'

    

    def cross_references(self,doc):
        objs = []
        for word in doc:
            if word.text in cross_references_list:
                # print(word.text)
                if word.i + 1 < len(doc) and doc[word.i + 1].text.replace('.','',1).isdigit():
                    # print(doc[word.i + 1].text)
                    objs.append({
                                'token':word.text,
                                'start':word.idx,
                                'stop':word.idx + len(word.text),
                                'change':cross_references_list[word.text]
                        })
                if word.i + 1 < len(doc) and doc[word.i + 1].text == '.':
                    # print(word.text, doc[word.i+1].text)
                    if word.i + 2 < len(doc) and doc[word.i + 2].text.replace('.','',1).isdigit():
                        if word.i + 3 < len(doc) and doc[word.i + 3].text.lower() == 'and':
                            if word.i + 4 < len(doc) and doc[word.i + 4].text.replace('.','',1).isdigit():
                                if cross_references_list[word.text][-1] != 's':
                                    objs.append({
                                                'token':'{}'.format(word.text, doc[word.i + 1]),
                                                'start':word.idx,
                                                'stop':word.idx + len(word.text) + len(doc[word.i + 1].text) + 1,
                                                'change':cross_references_list[word.text] + 's'
                                        })
                                else:
                                    objs.append({
                                            'token':'{}'.format(word.text, doc[word.i + 1]),
                                            'start':word.idx,
                                            'stop':word.idx + len(word.text) + len(doc[word.i + 1].text) + 1,
                                            'change':cross_references_list[word.text]
                                    })
                                    
                        else:
                            objs.append({
                                        'token':'{}'.format(word.text, doc[word.i + 1]),
                                        'start':word.idx,
                                        'stop':word.idx + len(word.text) + len(doc[word.i + 1].text) + 1,
                                        'change':cross_references_list[word.text]
                                })
                            
        return objs






    def transform(self, add_all, del_all, com_all):
        # self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []
        docs = self._get_spacy_docs()

        for idx, doc in enumerate(docs):
            obj = self.cross_references(doc)

            _temp_add, _temp_del, _temp_com = [], [], []
            for item in obj:
                if item['change'] != item['token']:
                    start, stop = self._map_span((item['start'], item['stop']), self._span_maps[idx])
                    add_map = self._return_add_map(pos=stop, token=item['change'])
                    del_map = self._return_del_map(start=start, stop=stop, token=self._sent_list[idx][start:stop])
                    if self.check_existent_map(add_map, add_all[idx]) and self.check_existent_map(del_map, del_all[idx]):
                        continue
                    self._num_errors += 1
                    _temp_del.append(del_map)
                    _temp_add.append(add_map)

            add_.append(_temp_add)
            del_.append(_temp_del)
            com_.append([])

        return add_, del_, com_