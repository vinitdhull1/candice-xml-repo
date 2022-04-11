from .base import Model
from ..__commons__ import LOGGER_NAME
import logging

logger = logging.getLogger(LOGGER_NAME)
from ..__commons__ import nlp
import string



next_list = ['figure','table','scheme', 'chart', 'box', 'section', 'appendix',
            'equation', 'model', 'step', 'panel', 'theorem', 'lemma', 'corollary', 'proof', 'algorithm',
            'figures','tables','schemes', 'charts', 'boxes', 'sections', 'appendixes',
            'equations', 'models', 'steps', 'panels', 'theorems', 'lemmas', 'corollaries', 'proofs', 'algorithms']
all_alpha = list(string.ascii_lowercase)

remove_words = ['above', 'below', 'following', 'previous']

class THE(Model):
    """
    --> Replaces wrong uses of indefinite articles on the basis of phonetics and other stuff
    """

    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'definite_article'
        self._type = 'grammar'

    @staticmethod
    def __correct_the(doc):
        idx = 0
        count = 0
        the_errors = []

        for word in doc:
            n2_w = None

            if word.text.lower() == 'the':
                try:
                    next_w = doc[idx + 1]

                except:
                    idx += 1
                    continue

                try:
                    n2_w = doc[idx + 2]

                except:
                    pass
                
                try:
                    n3_w = doc[idx + 3]

                except:
                    pass

                # NOUN + NUM for e.g. room 221

                if next_w.text.lower() in next_list :
                    
                    try:
                        if n2_w.pos_ == 'NUM' or  n2_w.text.lower()  in all_alpha:
                            the_errors.append({'start': word.idx, 'stop': word.idx + 3, 'token': 'the'})

                    except:
                        pass

                if next_w.text.lower() in remove_words:
                    try:
                        if n2_w.text.lower() in next_list:
                            if n3_w.text.lower()  in all_alpha or  n3_w.pos_ == 'NUM':
                                the_errors.append({'start': word.idx, 'stop': next_w.idx + len(next_w.text), 
                                    'token':"{} {}".format(word.text, next_w.text)})
                    except:
                        pass
                    
            idx += 1
        return the_errors

    def transform(self, add_all, del_all, com_all):
        # self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []

        docs = self._get_spacy_docs()

        for idx, doc in enumerate(docs):
            obj = THE.__correct_the(doc)
            _temp_add, _temp_del, _temp_com = [], [], []
            for item in obj:
            
                start, stop = self._map_span((item['start'],item['stop']), self._span_maps[idx])
                del_map = self._return_del_map(start=start, stop=stop, token=item['token'])
                if self.check_existent_map(del_map, del_all[idx]):
                    continue
                self._num_errors += 1
                _temp_del.append(del_map)
            add_.append([])
            del_.append(_temp_del)
            com_.append([])

        return add_, del_, com_
