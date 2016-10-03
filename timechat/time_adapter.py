from chatterbot.adapters.logic import LogicAdapter
import random
from chatterbot.conversation import Statement

class TimeAdapter(LogicAdapter):
    responses = {
        'en': [
            u"{Prep} {location} it is now: {time}.",
            u"The local time {prep} {location} is {time}.",
            u"{Prep} {location} the local time is {time}.",
            u"{time} is the local time {prep} {location}.",
        ],
        'nl': [
            u"{Prep} {location} is het nu {time}.",
            u"{Prep} {location} is de lokale tijd {time}.",
            u"{time} is de lokale tijd {prep} {location}."
        ]
    }

    keywords = {
        'en': ['time'],
        'nl': ['tijd', 'laat']
    }

    def __init__(self, api, **kwargs):
        super(TimeAdapter, self).__init__(**kwargs)
        self.api = api

    def can_process(self, statement):
        return True

    def get_response(self, lang, location, time, preposition):
        if lang not in self.responses:
            return ""
        
        sentence = random.choice(self.responses[lang])
        return sentence.format(
            location=location,
            time=time.strftime(u"%H:%M"),
            prep=preposition,
            Prep=preposition.title())

    def get_confidence(self, lang, tokens):
        if lang not in self.keywords:
            return 0
        
        for keyword in self.keywords[lang]:
            if keyword in tokens: return 1
        return 0
        
class FallbackAdapter(LogicAdapter):
    def can_process(self, stmt): return True
    def process(self, stmt):
        return 0.1, Statement("Sorry, I don't understand your question.")
