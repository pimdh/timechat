from flask import Flask, request, render_template, abort

import chatterbot
from chatterbot.conversation import Statement
from timechat import IdfTimeAdapter, EntityTimeAdapter, SyntaxTimeAdapter, FallbackAdapter, Api

chatbots = {}
api = Api()
for method, adapter_class in [
        ('idf', IdfTimeAdapter),
        ('entity', EntityTimeAdapter),
        ('syntax', SyntaxTimeAdapter)]:
    chatbot = chatterbot.ChatBot(
        'TimezoneChatBot',
        logic_adapters=[]
    )
    adapter = adapter_class(api)
    if method == 'idf':
        adapter.load_models('models.pickle')
    chatbot.logic.add_adapter(adapter)
    chatbot.logic.add_adapter(FallbackAdapter())
    chatbots[method] = chatbot
    
app = Flask(__name__)

@app.route("/", defaults={'method':'idf'}, methods=['GET'])
@app.route("/<method>", methods=['GET'])
def index(method):
    if method not in chatbots: abort(404)
    return render_template('index.html', method=method)

@app.route("/handle/<method>", methods=['POST'])
def handle(method):
    if method not in chatbots: abort(404)
    chatbot = chatbots[method]

    input = request.form['input']
    response = chatbot.get_response(Statement(input)).text
    return response

if __name__ == "__main__":
    app.run()
