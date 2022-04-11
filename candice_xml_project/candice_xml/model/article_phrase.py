from .base import Model
from ..__commons__ import LOGGER_NAME
import logging

logger = logging.getLogger(LOGGER_NAME)
from ..__paths__ import PATH_TO_RESOURCES
from ..__parameters__ import word_tokenizer
import pandas as pd
from .spelling_us_uk import US_UK



def read_phrase_article_list():
    """
    --> Read phrase article csv
    :return
    """
    df = pd.read_csv(PATH_TO_RESOURCES.joinpath('phrase_article.csv').as_posix())
    df['old'] = df['words'].apply(lambda x: x.lower().strip())
    df['new'] = df['modified'].apply(lambda x: x.lower().strip())

    new_phrase = dict(zip(df['old'].tolist(), df['new'].tolist()))

    return new_phrase


class ArticlePhrase(Model):
    """
    --> Finds prefixes, deletes hyphens, and joins such words.
    -->
    """

    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'article_phrase'
        self._type = 'grammar'

    def _get_article(self, doc):
        objs = []
        #logger.info(doc)
        all_phrases = read_phrase_article_list()
        for idx, word in enumerate(doc):
            try:
                new_word =  "{} {} {}".format(word, doc[idx+1], doc[idx+2])
                new_word2 = "{} {}{}{} {}".format(word, doc[idx+1], doc[idx+2], doc[idx+3], doc[idx+4])
                if new_word.lower() in all_phrases:
                    change = all_phrases[new_word.lower()]
                    if new_word[0].isupper():
                        change = all_phrases[new_word.lower()].capitalize()

                    objs.append({
                        'token': new_word,
                        'start': word.idx,
                        'stop': doc[idx + 2].idx + len(doc[idx + 2].text),
                        'change': change
                    })
                elif new_word2.lower() in all_phrases:
                    change = all_phrases[new_word2.lower()]
                    if new_word2[0].isupper():
                        change = all_phrases[new_word2.lower()].capitalize()
                    objs.append({
                        'token': new_word2,
                        'start': word.idx,
                        'stop': doc[idx + 4].idx + len(doc[idx + 4].text),
                        'change': change
                    })

            except:
                pass
        return objs

    def transform(self, add_all, del_all, com_all):
        self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []
        docs = self._get_spacy_docs()

        for idx, doc in enumerate(docs):
            obj = self._get_article(doc)
            _temp_add, _temp_del, _temp_com = [], [], []
            for item in obj:
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
