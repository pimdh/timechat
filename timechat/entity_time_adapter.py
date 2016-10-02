from time_adapter import TimeAdapter
from chatterbot.conversation import Statement
import nltk

class EntityTimeAdapter(TimeAdapter):
    def process(self, statement):
        result = self.api.call_entities(statement.text)

        if not result: return 0, Statement("")

        locations = [x for x in result['entities'] if x['type'] == 'LOCATION']

        if not locations: return 0, Statement("")

        location = max(locations, key=lambda x: x['salience'])['name']
        lang = 'en'
        prep = 'in'

        location, time = self.api.fetch_location_data(location, lang)

        if not location: return 0, Statement("")

        response = self.get_response(lang, location, time, prep)
        tokens = nltk.word_tokenize(statement.text)
        confidence = self.get_confidence(lang, tokens)

        return confidence, Statement(response)
