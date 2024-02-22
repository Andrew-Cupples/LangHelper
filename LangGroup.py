# This class holds the word groups
class LangGroup:
    # initiate the object, set the name and the words
    def __init__(self, name, words):
        self.setName(name)
        self.setWords(words)

    # get the words
    def getWords(self):
        return self.words
    
    # get the group name
    def getName(self):
        return self.name
    
    # set the name 
    def setName(self, name):
        self.name = name
    
    # set the words
    def setWords(self, words):
        self.words = words
    
    # add a word to the group
    def addWord(self, word):
        self.getWords().append(word)
