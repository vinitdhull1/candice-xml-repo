#-*- coding: utf-8 -*-

from .base import Model
from ..__commons__ import LOGGER_NAME, nlp_trf
import logging

logger = logging.getLogger(LOGGER_NAME)
from ..__paths__ import PATH_TO_RESOURCES
import re

from ..__parameters__ import sentence_tokenizer


# number_regex = r'\s+\d+\s+'
# start_number_regex = r'^\d+\s+'
# end_number_regex = r'\s+\d+$'
number_regex = r'([^\.]\s+)(\d+)(\s+[^\.])'

range_regex = r'\s+\d+(\s*-+\s*|\s*to\s*)\d+\s'

validLetters = "abcdefghijklmnopqrstuvwxyz"
vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"
units_list = []

def is_si_unit_word(word):
    if len(word) == 1 and (word != 'a'):
        if word.isalpha():
            return True
        else:
            return False
    else:
        if word in units_list:
            return True
        for char in word.lower():
            if char not in validLetters:
                return True
        

        num_vowel = 0
        num_consonant = 0
        for char in word.lower():
            if char in vowels:
                num_vowel += 1
            else:
                num_consonant += 1
        if num_vowel == len(word) or num_consonant == len(word):
            return True
        
        
                
        return False

def change_token(token):
    match = re.search(r'\s*-\s*-*\s*',token)
    if match:
        new_token = ''
        new_token += token[0:match.span()[0]]
        new_token += str('\u2013')
        new_token += token[match.span()[1]:]
        return new_token
    else:
        match = re.search(r'\s*to\s*',token)
        if match:
            new_token = ''
            new_token += token[0:match.span()[0]]
            new_token += str('\u2013')
            new_token += token[match.span()[1]:]
            return new_token
        else:
            return token



class NumberCorrections(Model):
    """
        Converting numbers less than 10 to string form.

        Also converting range to en dash

    """

    def __init__(self,
                *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'number_corrections'
        self._type = 'punctuation'


    def num_changes(self,doc):
        digit_dict = {0:'zero',1:'one',2:'two',
             3:'three',4:'four',5:'five',
             6:'six',7:'seven',8:'eight',
             9:'nine',10:'ten'}

        objs = []
        sentences = sentence_tokenizer.tokenize(doc.text)
        escape_list = ['fig', 'figs','figure','figures','fig.','section',
                        'sec','sec.','sections','chapter','chap','chap.',
                        'chapters','tables','table','tab.','equation',
                        'equations','eq.','eq']

        digits = []
        start_spans = []
        matches = re.finditer(number_regex,doc.text)
        for match in matches:
            digits.append(int(match.group()[2:-2]))
            start_spans.append(match.span()[0] + 2)

        last_idx = 0
        # sentence = doc.text
        # small_doc = doc
        for sentence in sentences:
            small_doc = nlp_trf(sentence)
        
        
            # print(small_doc.text, digits)
            if digits:
                if max(digits) > 10:
                    pass
                else:
                    for word in small_doc:
                        if (word.idx + last_idx) in start_spans:
                            flag = True
                            if word.i + 1 < len(small_doc):
                                next_word = (small_doc[word.i+1].text)
                                if is_si_unit_word(next_word):
                                    flag = False
                            
                            if word.i - 1 > 0 and \
                                small_doc[word.i - 1].text.lower() in escape_list:
                                flag = False

                            if len(small_doc) < 3:
                                flag = False

                            if word.i - 1 > 0 and doc[word.i-1].pos_ == "SYM":
                                flag = False
                            elif word.i + 1 < len(doc) and doc[word.i+1].pos_ == "SYM":
                                flag = False

                            # print(word.text,flag)
                            if word.i == 0 and flag:
                                objs.append({
                                    'token': '{}'.format(word.text),
                                    'start': word.idx + last_idx,
                                    'stop': word.idx + len(word.text) + last_idx ,
                                    'change': '{}'.format(digit_dict[int(word.text)].capitalize())
                                })
                            else:
                                if flag:
                                    objs.append({
                                        'token': '{}'.format(word.text),
                                        'start': word.idx + last_idx,
                                        'stop': word.idx + len(word.text) + last_idx ,
                                        'change': '{}'.format(digit_dict[int(word.text)])
                                    })

                        
                last_idx += small_doc[-1].idx + len(small_doc[-1].text) + 1
        # sentences = sentence_tokenizer.tokenize(doc.text)
        # objs = []
        # last_idx = 0
        # for sentence in sentences:
        #     small_doc = nlp(sentence)
            
        #     text_digits = []
        #     for word in small_doc:
        #         if word.text.isdigit():
        #             text_digits.append(int(word.text))
            
        #     if text_digits:
                
        #         if(small_doc[0].text.isdigit()):
        #             if int(small_doc[0].text) in digit_dict:
        #                 objs.append({
        #                             'token': '{}'.format(small_doc[0].text),
        #                             'start': small_doc[0].idx + last_idx,
        #                             'stop': small_doc[0].idx + len(small_doc[0].text) + last_idx ,
        #                             'change': '{}'.format(digit_dict[int(small_doc[0].text)].capitalize())
        #                         })
                
        #         if max(text_digits)>10:
        #             pass
        #         else:
        #             for word in small_doc:
        #                 if word.text.isdigit() and word.i != 0:
        #                     if word.i - 1 > 0 and small_doc[word.i-1].pos_ == "SYM":
        #                         pass
        #                     # else:
        #                     #     if int(word.text) in digit_dict:
        #                     #         if word.i + 1 < len(small_doc):
        #                     #             next_word = (small_doc[word.i+1].text)
        #                     #             if is_si_unit_word(next_word):
        #                     #                 pass
        #                     #             else:
        #                     #                 objs.append({
        #                     #                         'token': '{}'.format(word.text),
        #                     #                         'start': word.idx + last_idx,
        #                     #                         'stop': word.idx + len(word.text) + last_idx ,
        #                     #                         'change': '{}'.format(digit_dict[int(word.text)])
        #                     #                     })
        #                     #         else:
                                    
        #                     #             objs.append({
        #                     #                         'token': '{}'.format(word.text),
        #                     #                         'start': word.idx + last_idx,
        #                     #                         'stop': word.idx + len(word.text) + last_idx ,
        #                     #                         'change': '{}'.format(digit_dict[int(word.text)])
        #                     #                     })



        #     last_idx += small_doc[-1].idx + len(small_doc[-1].text) + 1
        return objs


    def range_changes(self,doc):

        objs = []
        # range_regex = r'\s+\d+(\s*[a-z]*\s*-\s*-*\s*|\s*to\s*)\d+\s'
        range_regex = r'\s\d+(\s{0,1}-\s{0,1}|\s{0,1}to\s{0,1})\d+[\s,]'


        # print(doc.text)
        matches = re.finditer(range_regex,doc.text)

        tokens = []
        start_spans = []
        end_spans = []
        for match in matches:
            tokens.append(match.group())
            start_spans.append(match.span()[0]+1)
            end_spans.append(match.span()[1] - 1)

        # if matches:
            # print(tokens)
            # print(doc.text)

            
        new_start_span = []
        new_end_span = []
        new_tokens = []

        i = 0
        for word in doc:
            if i < len(start_spans):
                if word.idx == start_spans[i]:
                    # flag = True
                    # for indx in range(word.i, len(doc)):
                    #     if not(doc[indx].text.isalnum()):
                    #         flag = False
                    #     if doc[indx].text in [',','?','!']:
                    #         break
                    if word.i - 1 > 0 and (doc[word.i - 1].text not in ['between','from','-']) \
                        and doc[word.i - 1].text != '.':

                        # if flag:
                        new_start_span.append(start_spans[i])
                        new_end_span.append(end_spans[i])
                        new_tokens.append(tokens[i])

                    # case where sentence starts with numeric range
                    if word.i - 1 > 0 and doc[word.i - 1].text == '.':
                        if word.i - 2 > 0 and not(doc[word.i - 2].text.isnumeric()) \
                            and doc[word.i - 2].text[0].isupper():
                            new_start_span.append(start_spans[i])
                            new_end_span.append(end_spans[i])
                            new_tokens.append(tokens[i])

                    # case which is decimal
                    if word.i - 1 > 0 and doc[word.i - 1].text == '.':
                        if word.i - 2 > 0 and doc[word.i - 2].text.isnumeric():
                            if word.i - 3 > 0 and doc[word.i - 3].text not in ['between','from','-']:
                                if word.i - 4 > 0 and doc[word.i - 4].text not in ['between','from','-']:
                                    new_start_span.append(start_spans[i])
                                    new_end_span.append(end_spans[i])
                                    new_tokens.append(tokens[i])
                    i += 1

        for idx,one_token in enumerate(new_tokens):
            # print(one_token)
            objs.append({
                        'token':one_token,
                        'start':new_start_span[idx],
                        'stop':new_end_span[idx],
                        'change': change_token(one_token).strip()
                })


        #decimal_range_regex = r'\s+\-*\d+.\d+(\s*[a-z]*\s*-\s*-*\s*|\s*to\s*)\d+.\d+'

        # sentences = sentence_tokenizer.tokenize(doc.text)
        # objs = []
        # last_idx = 0
        # for sentence in sentences:
        #     small_doc = nlp(sentence)
            
        #     for word in small_doc:
        #         if word.i + 2 < len(small_doc):
        #             first = word.pos_
        #             second = small_doc[word.i+1]
        #             third = small_doc[word.i+2].pos_
                    
        #             if first == "NUM":
        #                 if second.pos_ == "SYM":
        #                     if third == "NUM":
        #                         # print(word,second,small_doc[word.i+2].text)
        #                         objs.append({
        #                                     'token': '{}{}{}'.format(word,second,small_doc[word.i+2].text),
        #                                     'start': word.idx + last_idx,
        #                                     'stop': word.idx + len(word.text) + len(second.text) +
        #                                             len(small_doc[word.i+2].text) + last_idx ,
        #                                     'change': '{}{}{}'.format(word,str('\u2013'),small_doc[word.i+2].text)
        #                                 })
        #             if first == "NUM":          
        #                 if second.text.lower() == 'to':
        #                     if word.i - 1 > 0 and small_doc[word.i - 1].text.lower() != 'from':
        #                         if third == "NUM":
        #                             # print(word,second,small_doc[word.i+2].text)
        #                             objs.append({
        #                                         'token': '{}{}{}'.format(word,second,small_doc[word.i+2].text),
        #                                         'start': word.idx + last_idx,
        #                                         'stop': word.idx + len(word.text) + len(second.text) +
        #                                                 len(small_doc[word.i+2].text) + last_idx ,
        #                                         'change': '{}{}{}'.format(word,str('\u2013'),small_doc[word.i+2].text)
        #                                     })
                                
        #     last_idx += small_doc[-1].idx + len(small_doc[-1].text) + 1
        return objs

    def transform(self, add_all, del_all, com_all):
        self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []
        docs = self._get_spacy_docs()

        for idx, doc in enumerate(docs):
            obj = self.range_changes(doc)

            # obj.extend(self.num_changes(doc))
            # print(obj)
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
