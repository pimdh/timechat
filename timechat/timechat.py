#!/usr/bin/env python
# -*- coding: utf-8 -*-

import chatterbot
from chatterbot.conversation import Statement

def c(models, s):
    chatbot = chatterbot.ChatBot(
        'TiemzoneChatBot',
        logic_adapters=[]
    )
    adapter = TimeLogicAdapter(models)
    chatbot.logic.add_adapter(adapter)
    chatbot.logic.add_adapter(FallbackAdapter())
    response = adapter.process(Statement(s))
    print(response[0], response[1].text)

    #print(chatbot.get_response(s).text)
