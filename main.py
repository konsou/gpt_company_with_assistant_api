from OpenAIAssistant import OpenAIAssistant

if __name__ == '__main__':
    ass = OpenAIAssistant(model='gpt-4-0125-preview', name='Erkki',
                          instructions="You answer the user's questions in haiku form")
    response = ass.get_response(asker_name='konso', query="Who's the president of France?")
    print(response)

