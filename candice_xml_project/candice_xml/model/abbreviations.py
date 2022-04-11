from .base import Model
from ..__commons__ import LOGGER_NAME
import logging

logger = logging.getLogger(LOGGER_NAME)
from ..__paths__ import PATH_TO_RESOURCES
from ..__parameters__ import word_tokenizer, sentence_tokenizer
import pandas as pd
from .spelling_us_uk import US_UK
import re



def read_abbreviation_title_list():
    """
    --> Read abbreviation title csv
    :return
    """
    df = pd.read_csv(PATH_TO_RESOURCES.joinpath('abbreviation_title.csv').as_posix())
    df['old'] = df['word'].apply(lambda x: x.lower().strip())
    df['new'] = df['replace'].apply(lambda x: x.lower().strip())

    us_to_uk = dict(zip(df['old'].tolist(), df['new'].tolist()))
    uk_to_us = dict(zip(df['new'].tolist(), df['old'].tolist()))

    return us_to_uk, uk_to_us


class Abbreviations(Model):
    """
    --> Check the Article phrase and replace it with correct phrase.
    -->
    """

    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'abbreviation_rule'
        self._type = 'grammar'




    # def capital_abbreviations(self,doc):
    #     """
    #         Capitalized acronyms do not use periods (full stops).
    #     """
    #     capital_regex = r'\s[A-Z]\s\.(\s[A-Z]\s\.)+\s'
    #     objs = []
    #     matches = re.finditer(capital_regex,doc.text)
    #     # print(matches)
    #     print(doc)
    #     for match in matches:
    #         print(match.group())
    #         span = match.span()
    #         word = match.group()
            
    #         change_word = word.replace(".","").replace(" ","")
    #         objs.append({
    #                     'token':word.strip(),
    #                     'start':span[0] + 1,
    #                     'stop':span[1] - 1,
    #                     'change':change_word
    #         })
    #     return objs


    def _abbreviation_title(self, doc):
        """
        US: contractions (i.e. words minus their middle parts but still with their final letter) should end with a period (full stop)
        UK: do not end contractions (i.e. words minus their middle parts but still with their final letter) with a period (full stop).
        """
        
        us_to_uk, uk_to_us = read_abbreviation_title_list()
        us_uk = US_UK(sent_list=self._sent_list, doc_name=self._doc_name)
        us_uk_type = us_uk._find_majority()
        objs = []
        for idx, word in enumerate(doc):
            if us_uk_type == 'us':
                try:
                    if "{}{}".format(word.text, doc[idx+1].text).lower() in us_to_uk:
                        objs.append({
                            'token': "{}{}".format(word.text, doc[idx+1].text),
                            'start': word.idx,
                            'stop': doc[idx+1].idx + len(doc[idx+1].text),
                            'change': word.text
                            })
                    if "{}{}{}".format(word.text, doc[idx+1].text,  doc[idx+2].text).lower() in us_to_uk:
                        objs.append({
                            'token': "{}{}{}".format(word.text, doc[idx+1].text, doc[idx+2].text),
                            'start': word.idx,
                            'stop': doc[idx+2].idx + len(doc[idx+2].text),
                            'change':"{}{}".format(word.text,  doc[idx+2].text)
                            })
                except:
                    pass

            if us_uk_type == 'uk':
                if word.text.lower() in uk_to_us:
                    if idx+1 < len(doc):
                        if doc[idx+1].text != '.':
                            objs.append({
                                'token': word.text ,
                                'start': word.idx,
                                'stop': word.idx + len(word.text),
                                'change': "{}.".format( word.text)
                            })

            if word.text.lower() in ['inc','co','mass']:
                if doc[idx-1].pos_ in ["PROPN", "NOUN"]:
                    if idx+1 < len(doc):
                        if doc[idx+1].text not in  ['.', '-']:
                            objs.append({
                                'token': word.text ,
                                'start': word.idx,
                                'stop': word.idx + len(word.text),
                                'change': "{}.".format( word.text)
                            })

        return objs

    def _get_designation(self,doc):
        objs = []
        for idx, word in enumerate(doc):
            if idx+6 <= len(doc):
                flag = True
                if len(word.text) == 1 and word.text.isalpha() and doc[idx+1].text == '.' \
                    and len(doc[idx+2].text) == 1 and doc[idx+2].text.isalpha() \
                    and doc[idx+3].text == '.' and doc[idx+5].text != "." \
                    and doc[idx-1].text != "." :
                    if word.text.islower() and doc[idx+2].text.islower() \
                        and idx - 1 >= 0 and not(doc[idx-1].text.isnumeric()):
                        flag = False

                    if flag and "{}{}{}{}".format(word.text,doc[idx+1].text,doc[idx+2].text, doc[idx+3].text).lower() not in ["e.g.","i.e."] and word.text.isalpha() and doc[idx+2].text.isalpha(): 
                        if (doc[idx+4].pos_ not in ['PROPN', 'NOUN']) and ( (idx - 1 > 0) \
                                                and (doc[idx-1].pos_ not in ['PROPN','NOUN'])):
                            if not(doc[idx+4].text[0].isupper()):
                                objs.append({
                                    'token': "{}{}{}{}".format(word.text,doc[idx+1].text,doc[idx+2].text, doc[idx+3].text),
                                    'start': word.idx,
                                    'stop': doc[idx+3].idx + 1,
                                    'change':"{}{}".format(word.text,doc[idx+2].text)
                                    })
                            else:
                                objs.append({
                                    'token': "{}{}{}{}".format(word.text,doc[idx+1].text,doc[idx+2].text, doc[idx+3].text),
                                    'start': word.idx,
                                    'stop': doc[idx+3].idx + 1,
                                    'change':"{}{}.".format(word.text,doc[idx+2].text)
                                    })
                if len(word.text) == 1 and word.text.isalpha() and doc[idx+1].text == '.' \
                    and len(doc[idx+2].text) == 1 and doc[idx+2].text.isalpha() \
                    and doc[idx+3].text == '.' and len(doc[idx+4].text) == 1 \
                    and doc[idx+4].text.isalpha() and doc[idx+5].text == ".":

                    if word.text.islower() and doc[idx+2].text.islower() \
                        and doc[idx+4].text.islower() \
                        and idx - 1 >= 0 and not(doc[idx-1].text.isnumeric()):
                        flag = False
                    if flag and doc[idx+6].pos_ not in ['PROPN']:
                        if not(doc[idx+6].text[0].isupper()):
                            objs.append({
                                'token': "{}{}{}{}{}{}".format(word.text,doc[idx+1].text,doc[idx+2].text, doc[idx+3].text ,doc[idx+4].text,doc[idx+5].text ),
                                'start': word.idx,
                                'stop': doc[idx+5].idx + 1,
                                'change':"{}{}{}".format(word.text,doc[idx+2].text,doc[idx+4].text)
                                })
                        else:
                            objs.append({
                                'token': "{}{}{}{}{}{}".format(word.text,doc[idx+1].text,doc[idx+2].text, doc[idx+3].text ,doc[idx+4].text,doc[idx+5].text ),
                                'start': word.idx,
                                'stop': doc[idx+5].idx + 1,
                                'change':"{}{}{}.".format(word.text,doc[idx+2].text,doc[idx+4].text)
                                })    
        return objs



    def transform(self, add_all, del_all, com_all):
        #self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []
        docs = self._get_spacy_docs()

        for idx, doc in enumerate(docs):
            # obj = self.capital_abbreviations(doc)
            obj = self._get_designation(doc)
            # obj.extend(self._abbreviation_title(doc))
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
