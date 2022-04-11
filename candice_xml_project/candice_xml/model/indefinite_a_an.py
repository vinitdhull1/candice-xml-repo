from .base import Model
from ..__commons__ import LOGGER_NAME
import logging

logger = logging.getLogger(LOGGER_NAME)
from ..__paths__ import PATH_TO_RESOURCES
import re



# phonetics dic
pro_dict = {}  # Storing first letter of pronounciation
# Getting first alphabet of the pronounciation
file = open(PATH_TO_RESOURCES.joinpath('cmudict-0.7b.txt').as_posix(), "r", encoding='latin-1')
text = file.read()
text = text.split('\n')
idx = 0
for item in text:
    words = item.split(' ')
    try:
        pro_dict[words[0].lower()] = words[2][0]
    except:
        pass
    idx += 1

# 1 to one
ones = ["", "one ", "two ", "three ", "four ", "five ", "six ", "seven ", "eight ", "nine ", "ten ", "eleven ",
        "twelve ", "thirteen ", "fourteen ", "fifteen ", "sixteen ", "seventeen ", "eighteen ", "nineteen "]

twenties = ["", "", "twenty ", "thirty ", "forty ", "fifty ", "sixty ", "seventy ", "eighty ", "ninety "]

thousands = ["", "thousand ", "million ", "billion ", "trillion ", "quadrillion ", "quintillion ", "sextillion ",
             "septillion ", "octillion ", "nonillion ", "decillion ", "undecillion ", "duodecillion ", "tredecillion ",
             "quattuordecillion ", "quindecillion", "sexdecillion ", "septendecillion ", "octodecillion ",
             "novemdecillion ", "vigintillion "]


class A_AN(Model):
    """
    --> Replaces wrong uses of indefinite articles on the basis of phonetics and other stuff
    """

    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'indefinite_article'
        self._type = 'grammar'

    # Function to get numbers out of alpha-numeric
    @staticmethod
    def get_num(text):
        for match in re.finditer('(\d+)[^\s\d]+', text):
            return match.group(1)

        return False

    @staticmethod
    def __num999(n):
        c = n % 10  # singles digit
        b = ((n % 100) - c) / 10  # tens digit
        a = ((n % 1000) - (b * 10) - c) / 100  # hundreds digit
        t = ""
        h = ""
        a = int(a)
        b = int(b)
        c = int(c)
        if a != 0 and b == 0 and c == 0:
            t = ones[a] + "hundred "
        elif a != 0:
            t = ones[a] + "hundred and "
        if b <= 1:
            h = ones[n % 100]
        elif b > 1:
            h = twenties[b] + ones[c]
        st = t + h
        return st

    @staticmethod
    def __num2word(num):
        if num == 0: return 'zero'
        i = 3
        n = str(num)
        word = ""
        k = 0
        while i == 3:
            nw = n[-i:]
            n = n[:-i]
            if int(nw) == 0:
                word = A_AN.__num999(int(nw)) + thousands[int(nw)] + word
            else:
                word = A_AN.__num999(int(nw)) + thousands[k] + word
            if n == '':
                i = i + 1
            k += 1
        return word[:-1]

    @staticmethod
    def __check_upper(word):
        string = word.text
        for letter in string:
            if letter.isupper():
                return True
        return False

    @staticmethod
    def __correct_article_final(doc):
        idx = 0
        count = 0
        all_errors = []
        for sent in doc.sents:
            for word in sent:
                correction = {}
                flag = 0
                alphanum_flag = True
                if word.i + 1 < len(doc):

                    if doc[word.i+1].text == "SPACE":
                        if word.i + 2 < len(doc):
                            if(bool(re. match('^[a-zA-Z0-9]*$', doc[word.i+2].text)) == False):
                                alphanum_flag = False
                                # print(doc[word.i+2].text,alphanum_flag)
                    else:
                        if(bool(re. match('^[a-zA-Z0-9]*$', doc[word.i+1].text)) == False):
                            
                            alphanum_flag = False
                            # print(doc[word.i+1].text,alphanum_flag)

                if alphanum_flag and word.text == 'a':
                    w_range = doc[idx:idx + 5]  # to check for ';'
                    next_w = doc[idx + 1]
                    if next_w.pos_ != 'VERB' and next_w.pos_ != 'CCONJ':

                        letter = str(next_w)[0]
                        letter = letter.lower()

                        if str(next_w) == '“':
                            next_w = doc[idx + 2]
                            letter = str(next_w)[0]
                            letter = letter.lower()

                        caps = str(next_w)[0]

                        if ':' not in str(w_range):
                            try:
                                if next_w.is_upper or A_AN.__check_upper(next_w):
                                    idx += 1
                                    flag = 1
                                    continue

                                # print(next_w.text, next_w.text.isalnum())
                                # if not(next_w.text.isalnum()):
                                #     idx += 1
                                #     flag = 1
                                #     continue
                                    
                                if A_AN.get_num(str(next_w)):
                                    num = A_AN.get_num(str(next_w))
                                    n_word = A_AN.__num2word(num)
                                    n_word = n_word.split(' ')
                                    sound = pro_dict[n_word[0]]
                                    sound = sound.lower()
                                    if sound == 'a' or sound == 'e' or sound == 'i' or sound == 'o' or sound == 'u':
                                        correction = {'start': word.idx, 'stop': word.idx + 1, 'original': 'a',
                                                      'correct': 'an'}
                                        all_errors.append(correction)

                                elif next_w.is_digit:
                                    n_word = A_AN.__num2word(int(str(next_w)))
                                    n_word = n_word.split(' ')
                                    sound = pro_dict[n_word[0]]
                                    sound = sound.lower()
                                    if sound == 'a' or sound == 'e' or sound == 'i' or sound == 'o' or sound == 'u':
                                        correction = {'start': word.idx, 'stop': word.idx + 1, 'original': 'a',
                                                      'correct': 'an'}
                                        all_errors.append(correction)

                                else:
                                    sound = pro_dict[str(next_w).lower()]
                                    sound = sound.lower()
                                    if sound == 'a' or sound == 'e' or sound == 'i' or sound == 'o' or sound == 'u':
                                        correction = {'start': word.idx, 'stop': word.idx + 1, 'original': 'a',
                                                      'correct': 'an'}
                                        all_errors.append(correction)
                                        count += 1

                            except:
                                uni = str(next_w).lower()
                                if not uni.startswith('uni') and flag == 0:
                                    if letter == 'a' or letter == 'e' or letter == 'i' or letter == 'o' or letter == 'u':
                                        correction = {'start': word.idx, 'stop': word.idx + 1, 'original': 'a',
                                                      'correct': 'an'}
                                        all_errors.append(correction)

                elif alphanum_flag and word.text == 'an':
                    next_w = doc[idx + 1]
                    letter = str(next_w)[0]
                    letter = letter.lower()

                    if next_w.pos_ != 'VERB' and next_w.pos_ != 'CCONJ':
                        if str(next_w) == '“':
                            next_w = doc[idx + 2]
                            letter = str(next_w)[0]
                            letter = letter.lower()

                        caps = str(next_w)[0]

                        w_range = doc[idx - 5:idx + 5]  # to check for ';'
                        if ':' not in str(w_range):
                            try:
                                if next_w.is_upper or A_AN.__check_upper(next_w):
                                    idx += 1
                                    flag = 1
                                    continue

                                if A_AN.get_num(str(next_w)):
                                    num = A_AN.get_num(str(next_w))
                                    n_word = A_AN.num2word(num)
                                    n_word = n_word.split(' ')
                                    sound = pro_dict[n_word[0]]
                                    sound = sound.lower()
                                    if sound != 'a' and sound != 'e' and sound != 'i' and sound != 'o' and sound != 'u':
                                        correction = {'start': word.idx, 'stop': word.idx + 2, 'original': 'an',
                                                      'correct': 'a'}
                                        all_errors.append(correction)

                                elif next_w.is_digit:
                                    n_word = A_AN.__num2word(int(str(next_w)))
                                    n_word = n_word.split(' ')
                                    sound = pro_dict[n_word[0]]
                                    sound = sound.lower()
                                    if sound != 'a' and sound != 'e' and sound != 'i' and sound != 'o' and sound != 'u':
                                        correction = {'start': word.idx, 'stop': word.idx + 2, 'original': 'an',
                                                      'correct': 'a'}
                                        all_errors.append(correction)

                                else:
                                    sound = pro_dict[str(next_w).lower()]
                                    sound = sound.lower()
                                    if sound != 'a' and sound != 'e' and sound != 'i' and sound != 'o' and sound != 'u':
                                        correction = {'start': word.idx, 'stop': word.idx + 2, 'original': 'an',
                                                      'correct': 'a'}
                                        all_errors.append(correction)
                            except:
                                uni = str(next_w).lower()
                                if uni.startswith('uni') and flag == 0:
                                    correction = {'start': word.idx, 'stop': word.idx + 2, 'original': 'an',
                                                  'correct': 'a'}
                                    all_errors.append(correction)

                                if flag == 0 and letter != 'a' and letter != 'e' and letter != 'i' and letter != 'o' and letter != 'u':
                                    correction = {'start': word.idx, 'stop': word.idx + 2, 'original': 'an',
                                                  'correct': 'a'}
                                    all_errors.append(correction)
                idx += 1
        return all_errors

    def transform(self, add_all, del_all, com_all):
        self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []
        docs = self._get_spacy_docs()
        for idx, doc in enumerate(docs):
            obj = A_AN.__correct_article_final(doc)
            _temp_add, _temp_del, _temp_com = [], [], []
            for item in obj:
                
                start, stop = self._map_span((item['start'], item['stop']), self._span_maps[idx])
                add_map = self._return_add_map(pos=stop, token=item['correct'])
                del_map = self._return_del_map(start=start, stop=stop, token=item['original'])
                if self.check_existent_map(add_map, add_all[idx]) and self.check_existent_map(del_map, del_all[idx]):
                    continue
                self._num_errors += 1
                _temp_add.append(add_map)
                _temp_del.append(del_map)
            add_.append(_temp_add)
            del_.append(_temp_del)
            com_.append([])

        return add_, del_, com_
