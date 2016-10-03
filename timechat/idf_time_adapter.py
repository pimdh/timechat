from __future__ import division

import nltk
from chatterbot.adapters.logic import LogicAdapter
from chatterbot.conversation import Statement
import math
import cPickle

from api import Api
from time_adapter import TimeAdapter

class IdfTimeAdapter(TimeAdapter):
    LENGTH_PENALTY = -1/2
    FALLBACK_LOCATION = "Amsterdam"
    FALLBACK_PREPOSITION = "in"
    LANGUAGE_FREQ_POWER = 1/3

    models = []
    
    def can_process(self, statement):
        return len(self.models) > 0

    def determine_language(self, tokens):
        best_score = -1
        best_lang = None

        for lang in self.models:
            word_freq = self.models[lang]['word']
            freqs = [word_freq.get(token, 0) for token in tokens]
            score = sum([math.pow(x, self.LANGUAGE_FREQ_POWER) for x in freqs])/ \
                    math.pow(word_freq.N(), self.LANGUAGE_FREQ_POWER)

            if score > best_score:
                best_score = score
                best_lang = lang

        return best_lang

    def process(self, statement):
        text = statement.text.lower()
        tokens = nltk.word_tokenize(text)

        lang = self.determine_language(tokens)
        model = self.models[lang]

        pos = model['pos'].tag(tokens)
        prep_idxs = [i for i, (word, tag) in enumerate(pos) if tag == 'IN' or tag == 'prep']

        idfs = [1/model['word'].get(token, 10) for token in tokens]

        best_score = -1
        best_part = None
        best_prep = None
        
        n = len(tokens)
        for prep_idx in prep_idxs:
            i = prep_idx+1
            for j in range(i+1, n+1):
                part = tokens[i:j]

                idf_sum = sum(idfs[i:j])
                score = idf_sum * math.pow(j-i, self.LENGTH_PENALTY)

                if score > best_score:
                    best_score = score
                    best_part = part
                    best_prep = tokens[prep_idx]

        if best_score == -1:
            location = self.FALLBACK_LOCATION
        else:
            location = " ".join(best_part)

        location, time = self.api.fetch_location_data(location, lang)

        if not location:
            return 0, Statement("")

        if not best_prep:
            best_prep = self.FALLBACK_PREPOSITION

        response = self.get_response(lang, location, time, best_prep)
        confidence = self.get_confidence(lang, tokens)

        return confidence, Statement(response)

    def save_models(self, path):
        with open(path, 'wb') as f:
            cPickle.dump(self.models, f)

    def load_models(self, path):
        with open(path, 'rb') as f:
            self.models = cPickle.load(f)

    def build_models(self):
        def word_freq(corpus):
            return nltk.FreqDist((x.lower() for x in corpus))
        def pos_model(corpus):
            freq = nltk.ConditionalFreqDist(corpus)
            likely_tags = dict((word, freq[word].max()) for word in freq)
            return nltk.UnigramTagger(model=likely_tags)

        self.models = {
            'en': {
                'word': word_freq(nltk.text.TextCollection(nltk.corpus.gutenberg)),
                'pos': pos_model(nltk.corpus.brown.tagged_words())
            },
            'nl': {
                'word': word_freq(nltk.corpus.alpino.words()),
                'pos': pos_model(nltk.corpus.alpino.tagged_words())
            }        
        }
