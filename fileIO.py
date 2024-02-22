import numpy as np
import LangGroup
def writeToFile(langGroups, fileName):
    # Writing sentences to a file
    with open("outputs/" + fileName + ".txt", "w") as file:
        file.seek(0)

        # for every group of words
        for group in langGroups:
            
            # write the name, use # to track groups
            file.write('#' + group.getName() + "\n")
            
            # the write every word in the group, use $ to track words
            for index in range(len(group.getWords())):
                file.write("$" + group.getWords()[index] + "\n")

# Reading sentences from a file
def readFromFile(filepath):
    langGroups = []
    with open(f"outputs/{filepath}.txt", "r") as file:
        file.seek(0)
        # get the file in line format
        sentences_read = file.readlines()
        currentLangGroup = None
        # loop through
        for sentence in sentences_read:
            # make new group if # is found
            if sentence[0] == "#":
                currentLangGroup = LangGroup.LangGroup(sentence[1:-1], [])
                print(sentence[1:-1])
                langGroups.append(currentLangGroup)
            # add word to current group
            elif sentence[0] == "$":
                currentLangGroup.getWords().append(sentence[1:-1])

    return langGroups