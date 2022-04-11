from .base import Model
from ..__commons__ import LOGGER_NAME
import logging
from nltk.tokenize import word_tokenize
logger = logging.getLogger(LOGGER_NAME)
from ..__paths__ import PATH_TO_RESOURCES
from ..__parameters__ import sentence_tokenizer, word_tokenizer
from .__common__ import next_list, words_list, incorrect_word
import pandas as pd
from .spelling_us_uk import US_UK
import re
import string
import inflect
inflect = inflect.engine()

import hunspell
hobj = hunspell.HunSpell('/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff')


def check_all_caps_with_small_s(word):
    '''
    Check for words like CNTs, AGNWs for double plurals
    '''
    flag = True
    for idx,char in enumerate(word):
        if idx < len(word) - 1:
            if not(char.isupper()):
                flag = False
        if idx == len(word) - 1:
            if not(char.islower()) or char != 's':
                flag = False
    return flag



class Grammar(Model):

    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'new_grammar'
        self._type = 'punctuation'


    def _incorrect_word_order(self,doc):
        objs = []
        for idx, word in enumerate(doc):
            try:
                if "{} {}".format(word.text.lower(), doc[idx+1].text.lower()) in incorrect_word:
                    objs.append({
                        'token' : "{} {}".format(word.text, doc[idx+1].text),
                        'start' : word.idx,
                        'stop'  : doc[idx+1].idx + len(doc[idx+1].text),
                        'change': incorrect_word.get("{} {}".format(word.text.lower(), doc[idx+1].text.lower()))
                        })
            except:
                pass

            try:    
                if "{} {} {}".format(word.text.lower(), doc[idx+1].text.lower(), doc[idx+2].text.lower()) in incorrect_word:
                    objs.append({
                        'token' : "{} {} {}".format(word.text, doc[idx+1].text, doc[idx+2].text),
                        'start' : word.idx,
                        'stop'  : doc[idx+2].idx + len(doc[idx+2].text),
                        'change': incorrect_word.get("{} {} {}".format(word.text.lower(), doc[idx+1].text.lower(), doc[idx+2].text.lower()))
                        })
            except:
                pass

        return objs


    
    def _definite_article_in_equation(self, doc):
        """
        Check if first word is where after that select the first sentence 
        where there is words present in the list and add 'the' if that is not present after that

        """
        objs = []
        if doc and doc[0].text.lower() == "where":
            sentences = sentence_tokenizer.tokenize(doc.text)
            sent = sentences[0].split(" ")
            stop = 0
            for idx, word in enumerate(sent):
                if word.lower() in words_list:
                    if sent[idx+1].lower() != 'the':
                        objs.append({
                            'start': stop + len(word) + 1,
                            'stop' : stop + len(word) + 1 ,
                            'change' : 'the'
                            })
                stop += len(word)+1


        return objs



    def _indefinite_article_with_plural(self,doc):
        """
        Check if word after a, an is singular or plural. 
        If its plural change it to singular
        """
        objs = []
        flag = False
        exception = False
        for idx, word in enumerate(doc):
            if word.text in ['a','an']:
                singular = ''
                if idx + 1 < len(doc):
                    if doc[idx+1].pos_ == "SPACE":
                        if (idx + 2 < len(doc)) and \
                            (hobj.spell(doc[idx+2].text) or \
                            check_all_caps_with_small_s(doc[idx+2].text)):
                            flag = True
                            singular = inflect.singular_noun(doc[idx+2].text)
                    else:
                        if (hobj.spell(doc[idx+1].text) or \
                            check_all_caps_with_small_s(doc[idx+1].text)):
                            singular = inflect.singular_noun(doc[idx+1].text)

                if word.text == 'a' and singular == 'mean':
                    exception = True

                if singular in ['politic','physic','new','dynamic','mas']:
                    exception = True

                if singular and hobj.spell(singular) and not(exception):
                    if flag and (singular != doc[idx+2].text):

                        objs.append({
                            'token' : doc[idx+2].text,
                            'start' : doc[idx+2].idx,
                            'stop'  : doc[idx+2].idx + len(doc[idx+2].text),
                            'change': singular
                            })
                    else:
                        if (singular != doc[idx+1].text):
                            objs.append({
                                'token' : doc[idx+1].text,
                                'start' : doc[idx+1].idx,
                                'stop'  : doc[idx+1].idx + len(doc[idx+1].text),
                                'change': singular
                                })

        return objs
      

    def _get_capital(self,doc):
        """
    Where specific chapters, sections, figures, parts, tables, etc., are referred to in the text they 
        should take an initial cap, e.g. ‘Chapter 6’, ‘Section 1.3’. Use lower-case ‘c’ for references 
        to chapters in other books, e.g. ‘As Smith says in chapter 4 of his...?’ 
        """
        objs = []
        all_alpha = list(string.ascii_lowercase)
        for idx, word in enumerate(doc):
            if word.text in next_list:
                if len(doc) > idx+1:
                    if doc[idx+1].pos_ == 'NUM' or doc[idx+1].text.lower() in all_alpha:
                        if word.text == 'chapter' and  doc[idx+2].text.lower() in ['of']:
                            continue

                        else:
                            objs.append({
                                'token' : word.text,
                                'start' : word.idx,
                                'stop'  : word.idx + len(word.text),
                                'change': word.text.capitalize()
                            })

        return objs


    def _apostrophes_in_decades(self,doc):
        """
        Remove unnecessary apostrophes from decades, e.g. 1920s not 1920's.
        Do not abbreviate decades, e.g. 1960s not '60s.
        Decades can be spelled out, e.g. sixties.
        Apostrophes may follow decades where used to indicate possession, e.g. the 1960s' cohort. 
        """
        objs = []
        
        for idx, word in enumerate(doc):
            if idx+2 < len(doc):
                if word.pos_ == 'NUM' and word.text.isnumeric():
                    if doc[idx+1].text in ["'", "’", "‘"] and doc[idx+2].text == 's':
                         objs.append({
                                'token' : "{}{}{}".format(word.text,doc[idx+1].text, doc[idx+2].text),
                                'start' : word.idx,
                                'stop'  : doc[idx+2].idx + len(doc[idx+2].text),
                                'change': "{}{}".format(word.text, doc[idx+2].text)
                            })
                if word.text in ["'", "’", "‘"] and doc[idx+1].text in ['20s','30s','40s','50s','60s','70s','80s','90s']:
                    objs.append({
                                'token' : "{}{}".format(word.text,doc[idx+1].text),
                                'start' : word.idx,
                                'stop'  : doc[idx+1].idx + len(doc[idx+1].text),
                                'change': "19{}".format(doc[idx+1].text)
                            })


        
        return objs




    def transform(self, add_all, del_all, com_all):
        self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []
        docs = self._get_spacy_docs()

        for idx, doc in enumerate(docs):
            obj = self._apostrophes_in_decades(doc)
            # obj.extend(self._indefinite_article_with_plural(doc))
            # obj.extend(self._definite_article_in_equation(doc))
            obj.extend(self._incorrect_word_order(doc))
            obj.extend(self._get_capital(doc))
            _temp_add, _temp_del, _temp_com = [], [], []
            for item in obj:
            
                start, stop = self._map_span((item['start'], item['stop']), self._span_maps[idx])
                add_map = self._return_add_map(pos=stop, token=item['change'])
                del_map = self._return_del_map(start=start, stop=stop, token=self._sent_list[idx][start:stop])
                if self.check_existent_map(add_map, add_all[idx]) and self.check_existent_map(del_map, del_all[idx]):
                    continue
                self._num_errors += 1
                _temp_add.append(add_map)
                _temp_del.append(del_map)

            del_.append(_temp_del)
            add_.append(_temp_add)
            com_.append([])

        return add_, del_, com_
