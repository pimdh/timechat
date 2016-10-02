from time_adapter import TimeAdapter
from chatterbot.conversation import Statement

class SyntaxTimeAdapter(TimeAdapter):
    def process(self, statement):
        result = self.api.call_syntax(statement.text)

        if not result: return 0, Statement("")
        
        lang = result['language']
        tokens = result['tokens']

        tokens_text = [x['text']['content'] for x in tokens]
        
        children = {}
        for i, token in enumerate(tokens):
            parent = token['dependencyEdge']['headTokenIndex']
            if i == parent: continue
            parent_children = children.get(parent, [])
            parent_children.append(i)
            children[parent] = parent_children

        prepositions = []
        for i, prep in enumerate(tokens):
            if prep['partOfSpeech']['tag'] != 'ADP': continue
            preposition = [tokens[j] for j in self.traverse(children, i)][1:]
            preposition.sort(key=lambda x: x['text']['beginOffset'])
            preposition_text = [x['text']['content'] for x in preposition]
            prepositions.append((prep['text']['content'], preposition_text))

        prep, body = max(prepositions, key=lambda x: len(x[1]))
        location = " ".join(body)

        location, time = self.api.fetch_location_data(location, lang)

        if not location: return 0, Statement("")

        response = self.get_response(lang, location, time, prep)
        confidence = self.get_confidence(lang, tokens_text)

        return confidence, Statement(response)

    def traverse(self, children, node):
        res = [node]
        for child in children.get(node, []):
            res += self.traverse(children, child)
        return res
