from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI

# CURRENT API KEY
GOOGLE_API_KEY = ""

# This string is used to ensure the LLM doesn't use too advanced word
difMsg = "Make sure to not use any complicated words, this is for language learning purposes. So try to keep it as simple as possible"

# Initiate the LLM
def createLLM():
    return ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)

# Generate a response from the LLM given a prompt
def generateResponse(prompt, llm): 
    result = llm.invoke(prompt)
    return result.content

# Create the correct prompt based on user input
def callLLM(mode, words, language, history, llm, difficulty=difMsg):
    if mode == 1:
        return generateResponse(createParagraphPrompt(words, difficulty, language), llm)
    if mode == 2:
        response = generateResponse(createChatPrompts(words, difficulty, history, language), llm)
        return response
    if mode == 3:
        return generateResponse(createSentance(words, difficulty, language), llm)
    if mode == 4:
        return generateResponse(translateLastResponse(words, language), llm)
    if mode == 5:
        return generateResponse(createDefinitionPrompt(words, language), llm)
    if mode == 6:
        return generateResponse(askQuestion(words, language),llm)

# remove this
def commandCall(input, language, lastResponse, llm):
    commands = input.split(" ")
    if commands[0] == "def":
        return generateResponse(createDefinitionPrompt(commands, language), llm)
    if commands[0] == "help":
        # list commands
        return "Hello! To use the app first select a language then select a word group if you'd like to generate content. If you'd like to chat or define a word, click the button then enter your input in the prompt!"
    if commands[0] == "translate":
        return generateResponse(translateLastResponse(lastResponse, language), llm)

# The following create prompts for the LLM

# prompt used to translate word from language to english
def createDefinitionPrompt(words, language):
    str = ""
    for word in words[1:]:
        str += word + " "
    return f"""translate each of these words ({str}) from {language} into English. Output your answer in this format
    The word "word" is defined as "definition" Do not deviate from this structure. Do not output more definitions then words I give you."""

# translate the last response that the LLM gave
def translateLastResponse(response, language):
    return f"""Translate this response from {language} into English: {response}"""

# ask a general question
def askQuestion(question, language):
    return f"""Respond to this prompt: {question}. It is likely about {language} language. You response should be in English, do your best"""

# create a paragraph based on a word group
def createParagraphPrompt(words, difficulty, language):
    return f"""Here is your task: Using a 1-4 of these words {words}, create a 60 word paragraph in {language}. {difficulty}"""

# allows for the user to chat with the AI. It is given a history to make the chat flow better
def createChatPrompts(chat, difficulty, history, language):

    return f"""You are having a conversation in {language}. You are responding to this chat: {chat}. 
    Create a chat message in {language}. Here is the hisory of the chat: 
    Here is your chat History: {history}. Your messages are denoted by G: 
    and the other person is denoted User: (output the response ONLY. No USer: or G: )Focus more on making the conversation 
    make sense {difficulty}"""

# creates a sentance based on a word group
def createSentance(words, difficulty, language):
    return f"""Using a 1-3 of these words {words} create a 13 word sentance in {language}. {difficulty}"""
