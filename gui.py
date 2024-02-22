from PyQt6.QtWidgets import QStyleFactory, QMainWindow, QApplication, QWidget, QPushButton, QLabel, QTextEdit, QPlainTextEdit, QTreeView, QStyledItemDelegate
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem
import fileIO
import LangGroup
import LLM
import random
import sys

# This allows you to change the height of the tree items
class CustomDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(30)
        size.setWidth(30)
        return size

# Main window
class MainWindow(QMainWindow):

    # initiate the mainwindow
    def __init__(self):
        super().__init__()

        # set the central widget to add a background color
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        centralWidget.setStyleSheet("background-color: #344b9e;")

        # holds the current language
        self.lang = None
        
        # keeps track of the chat history
        self.chatHistory = ""

        # initiate the AI features
        self.init_aiPage()

        # create a group which the user can add new words to
        self.newGroup = LangGroup.LangGroup("New Words", [])
        
        # this array holds all the word groups
        self.mainGroups = []
        self.mainGroups.append(self.newGroup)

        # holds which group is selected
        self.selectedGroup = None

        # initiate the LLM
        self.llm = LLM.createLLM()

        # keep track of the last response the user gave
        self.lastResponse = ""

        # which mode is the program in, used to help with commands
        self.sysMode = 0

    # get the selected words based on which group is clicked
    def getSelectedItems(self, treeView):
        selected_indexes = treeView.selectedIndexes()
        if not selected_indexes:
            # return non if nothings selected
            return None
        for index in selected_indexes:
            item = index.data()
            print(f"data: {item}")
        return item
            
    # initiate the page
    def init_aiPage(self):
        self.setWindowTitle('Lang Helper')
        self.setGeometry(775, 35, 600, 1000)

        # these help make the UI line up correctly
        xShelf = 10
        yShelf = 40

        # create menu bar
        menubar = self.menuBar()

        # Create File menu
        switchMenu = menubar.addMenu('Select Language')

        # Add actions to File menu for every language

        # norwegian
        norwegianAction = QAction('Norwegian', self)
        switchMenu.addAction(norwegianAction)
        norwegianAction.triggered.connect(self.switchToNorwegian)

        # spanish
        spanishAction = QAction('Spanish', self)
        switchMenu.addAction(spanishAction)
        spanishAction.triggered.connect(self.switchToSpanish)

        # french
        frenchAction = QAction('French', self)
        switchMenu.addAction(frenchAction)
        frenchAction.triggered.connect(self.switchToFrench)

        # Add a separator in the menu
        switchMenu.addSeparator()

        # Label for the dictionary
        self.dictLabel = QLabel('Dictionary', self)
        self.dictLabel.setGeometry(xShelf + 30, yShelf + 25, 90, 20)
        self.dictLabel.setStyleSheet("font-size: 20px; color: #00c7c4")
         
        # the tree view holds the root item which stores all the groups for the user 
        self.treeView = QTreeView(self)
        self.model = QStandardItemModel()
        self.treeView.setModel(self.model)

        # holds tree
        self.rootItem = self.model.invisibleRootItem()
        # Expand all items by default
        self.treeView.expandAll()

        # Set the custom delegate to control item heights
        delegate = CustomDelegate()
        self.treeView.setItemDelegate(delegate)

        yShelf += 50
        self.treeView.setGeometry(xShelf, yShelf, 150, 400)
        self.treeView.setStyleSheet("font-size: 18px; background-color: #f0f5f5;")

        xShelf = 175
        yShelf = 550

        # This button generates a paragraph based on the selected words
        self.generateParagraphButton = QPushButton('Generate Paragraph', self)
        self.generateParagraphButton.setGeometry(xShelf, yShelf, 126, 40)
        self.generateParagraphButton.clicked.connect(lambda: self.genParagraph(self.llm))
        self.generateParagraphButton.setStyleSheet("font-size: 13px; background-color: #f0f5f5;")

        # This button allows you to have a conversation with the AI
        self.HaveAConvoButton = QPushButton('Have A Convo', self)
        self.HaveAConvoButton.setGeometry(xShelf + 127, yShelf, 126, 40)
        self.HaveAConvoButton.setStyleSheet("font-size: 13px; background-color: #f0f5f5;")
        self.HaveAConvoButton.clicked.connect(lambda: self.chatMode(self.llm))
        self.HaveAConvoButton.setCheckable(True)

        # This button generates a sentance based on the selected words
        self.generateSentanceButton = QPushButton("Generate Sentance", self)
        self.generateSentanceButton.setGeometry(xShelf + 254, yShelf, 126, 40)
        self.generateSentanceButton.clicked.connect(lambda: self.genSentance(self.llm))
        self.generateSentanceButton.setStyleSheet("font-size: 13px; background-color: #f0f5f5;")

        # This button translates the last output from the AI
        self.translateLastOutput = QPushButton("Translate Last Output", self)
        self.translateLastOutput.setGeometry(xShelf + 127, yShelf + 40, 126, 40)
        self.translateLastOutput.clicked.connect(lambda: self.genTranslation(self.llm))
        self.translateLastOutput.setStyleSheet("font-size: 13px; background-color: #f0f5f5;")
        
        # This button gives you a random cognate for the given language
        self.cognateButton = QPushButton("Get Random Cognate", self)
        self.cognateButton.setGeometry(xShelf, yShelf + 40, 126, 40)
        self.cognateButton.clicked.connect(lambda: self.getRandCognate())
        self.cognateButton.setStyleSheet("font-size: 13px; background-color: #f0f5f5;")

        # This button allows you to input a word to translate
        self.defineButton = QPushButton("Define Words", self)
        self.defineButton.setGeometry(xShelf + 254, yShelf + 40, 126, 40)
        self.defineButton.clicked.connect(lambda: self.defineWord(self.llm))
        self.defineButton.setStyleSheet("font-size: 13px; background-color: #f0f5f5;")

        yShelf = 90
        xShelf = 175
        
        # AI Output area
        self.AIOutputArea = QTextEdit(self)
        self.AIOutputArea.setGeometry(xShelf, yShelf, 380, 400)
        self.AIOutputArea.setReadOnly(True)
        # set text
        self.AIOutputArea.setText("Welcome to LangHelper! Select your language in the top left\n\n> Select a group from the dictionary and click a button to generate some output \n\n\n> Type '/help' for more info or just ask me a question!")
        
        # allign it vertically
        self.setVert()
        # set coloring
        self.AIOutputArea.setStyleSheet("font-size: 20px; background-color: #f0f5f5;")
        yShelf += 410

        # User prompt area
        self.UserInputArea = QPlainTextEdit(self)
        self.UserInputArea.setPlaceholderText("Talk to LangHelper here!")
        self.UserInputArea.installEventFilter(self)
        self.UserInputArea.setGeometry(xShelf, yShelf, 325, 40)
        self.UserInputArea.setStyleSheet("font-size: 14px; background-color: #f0f5f5;")

        # The enter button
        xShelf += 330
        self.enterButton = QPushButton('Enter', self)
        self.enterButton.setGeometry(xShelf, yShelf, 50, 40)
        self.enterButton.clicked.connect(lambda: self.handlePrompt())
        self.enterButton.setStyleSheet("font-size: 14px; background-color: #f0f5f5;")

        xShelf = 10
        yShelf = 500
        
        # This is where the user can add a word
        self.wordArea = QPlainTextEdit(self)
        self.wordArea.setPlaceholderText("add a word here")
        self.wordArea.installEventFilter(self)
        self.wordArea.setGeometry(xShelf, yShelf, 150, 40)
        self.wordArea.setStyleSheet("font-size: 14px; background-color: #f0f5f5;")

        # The button the user clicks to add a word to a group
        yShelf += 50
        self.addButton = QPushButton('Add Word', self)
        self.addButton.setGeometry(xShelf, yShelf, 150, 40)
        self.addButton.clicked.connect(lambda: self.addWord(self.wordArea.toPlainText()))
        self.addButton.setStyleSheet("font-size: 13px; background-color: #f0f5f5;")

        # This button saves the given dictionary to a file
        yShelf += 42
        self.saveDictButton = QPushButton('Save Dictionary', self)
        self.saveDictButton.setGeometry(xShelf, yShelf, 150, 38)
        self.saveDictButton.clicked.connect(lambda: self.updateFile(self.mainGroups, self.lang))
        self.saveDictButton.setStyleSheet("font-size: 13px; background-color: #f0f5f5;")

        # This is the big label at the bottom
        yShelf = 600
        self.langLabel = QLabel('LángHelpèr', self)
        self.langLabel.setGeometry(xShelf + 100, yShelf + 50, 400, 100)
        self.langLabel.setStyleSheet("font-size: 60px; font-weight: bold; color: #00c7c4;")
        return self

    # close the application
    def close(self):
        QApplication.instance().quit()

    # Used to get an event
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == 16777220 and isinstance(obj, QPlainTextEdit):
            self.handlePrompt()
            return True
        return super().eventFilter(obj, event)

    # Switches the language to norwegian and changes the dictionary
    def switchToNorwegian(self):
        langGroups = fileIO.readFromFile("norwegian")
        self.updateTree(langGroups)
        for group in langGroups:
            self.mainGroups.append(group)
        self.lang = "Norwegian"
        self.addToAIOutput("Switching to Norwegian")

    # Switches the language to Spanish and changes the dictionary
    def switchToSpanish(self):
        langGroups = fileIO.readFromFile("spanish")
        self.updateTree(langGroups)
        for group in langGroups:
            self.mainGroups.append(group)
        self.lang = "Spanish"
        self.addToAIOutput("Switching to Spanish")

    # Switches the language to French and changes the dictionary
    def switchToFrench(self):
        langGroups = fileIO.readFromFile("french")
        self.updateTree(langGroups)
        for group in langGroups:
            self.mainGroups.append(group)
        self.lang = "French"
        self.addToAIOutput("Switching to French")

    # Calls fileIO to write the dictionary to a file
    def updateFile(self, langGroups, fileName):
        if fileName != None:
            fileIO.writeToFile(langGroups, fileName)
    
    # adds a word to a dictionary
    def addWord(self, word):
        # make sure a language is selected first
        if self.selectFirst() == False:
            return
        # check if theres input
        if word != "":
            # get the group by the selected name
            name = self.getSelectedItems(self.treeView)
            if name == None or self.getGroupFromName(name) == None:
                self.newGroup.addWord(word)
            else:
                # add to the group if one was selected
                self.getGroupFromName(name).addWord(word)
            # update the dictionary
            self.updateTree(self.getLangGroups())
            # reset the area
            self.wordArea.setPlainText("")

    # update all the values in the tree
    def updateTree(self, langGroups):

        # remove all items first
        self.model.removeRows(0, self.rootItem.rowCount())

        # for every item in the groups, add them to the tree
        for group in langGroups:
            groupItem = QStandardItem(group.getName())
            self.rootItem.appendRow(groupItem)
            for word in group.getWords():
                # create the word item and add it to a group
                wordItem = QStandardItem(word)
                groupItem.appendRow(wordItem)

    # get the lang group
    def getLangGroups(self):
        return self.mainGroups
    
    # add a group
    def addLangGroup(self, langGroup):
        self.getLangGroups().append(langGroup)
        self.updateTree(self.getLangGroups())

    # merge groups
    def mergeGroup(self, groupNew, groupOld):
        groupNew.getWords().extend(groupOld.getWords())
        self.updateTree(self.getLangGroups())

    # get the group from its name
    def getGroupFromName(self, groupName):
        if groupName == None:
            return None
        for group in self.getLangGroups():
            if group.getName() == groupName:
                return group
        return None
    
    # get the group based on the selected group
    def getSelectedGroup(self):
        return self.getGroupFromName(self.getSelectedItems(self.treeView))
    
    # generate a paragraph from the words
    def genParagraph(self, llm):
        if self.selectFirst() == False:
            return
        # reset system mode
        self.sysMode = 0
        # error checking if no words are selected
        if self.getSelectedGroup() == None:
            self.AIOutputArea.setText(self.AIOutputArea.toPlainText() + "\n\n\n" + "> Click a group from the Dictionary to generate\n\n\n")
            self.setVert()
            return
        # call the LLM file with the given word array and language
        str = LLM.callLLM(1, self.getSelectedGroup().getWords(), self.lang, None, llm)
        # update output area
        self.addToAIOutput(str)
        # set this as the last response
        self.setLastResponse(str)
        # delete history
        self.handleHistory()

    # generate a sentance 
    def genSentance(self, llm):
        # error checking for if a language is selected
        if self.selectFirst() == False:
            return
        self.sysMode = 0
        # ensure a group is selected
        if self.getSelectedGroup() == None:
            self.AIOutputArea.setText(self.AIOutputArea.toPlainText() + "\n\n\n" + "> Click a group from the Dictionary to generate\n\n\n")
            self.setVert()
            return
        # call the llm
        str = LLM.callLLM(3, self.getSelectedGroup().getWords(), self.lang, None, llm)
        # add to output
        self.addToAIOutput(str)
        # set as last response
        self.setLastResponse(str)
        # reset history
        self.handleHistory()

    # translate the last response
    def genTranslation(self, llm):
        if self.selectFirst() == False:
            return
        self.sysMode = 0
        # error handling if there isn't a response to translate
        if self.lastResponse == "":
            self.AIOutputArea.setText(self.AIOutputArea.toPlainText() + "\n\n\n" + "> There isn't a response to translate yet\n\n\n")
            self.setVert()
            return
        # call the llm
        str = LLM.callLLM(4, self.lastResponse, self.lang, None, llm)
        self.addToAIOutput(str)
        self.setLastResponse("")
    
    # define a word
    def defineWord(self, llm):
        if self.selectFirst() == False:
            return
        # set system mode so the system knows to listen for the user to type a word
        self.sysMode = 1
        # update the output area to ask the user for a word
        self.AIOutputArea.setText(self.AIOutputArea.toPlainText() + "\n\n\n" + "> What word would you like me to define? \n\n\n")
        self.setVert()
        self.setLastResponse("")

    # get a random cognate
    def getRandCognate(self):
        if self.selectFirst() == False:
            return
        # norwegian cognates
        norwegianCognates = ["Aksent", "Animal", "Artist", "Banana", "Basis", "Bitter", "Brilliant", "Central", "Champion", 
        "Dynamisk", "Elegant", "Energi", "Fantastisk", "Gigantisk", "Hotel", "Identisk", "Internasjonal", "Kontakt", "Koselig", 
        "Kreativ", "Løft", "Magnetisk", "Museum", "Nasjon", "Normal", "Optimal", "Original", "Passion", "Perfekt", 
        "Plastikk", "Rapid", "Reform", "Sensitiv", "Sjokolade", "Stabil", "Talent", "Teater", "Tradisjon", "Typisk", 
        "Universitet", "Vitamin", "Xylofon", "Yoga", "Zoo", "Zone"
        ]
        # english translations
        translatedNorwegianCognates = ["Accent", "Animal", "Artist", "Banana", "Basis", "Bitter", "Brilliant", "Central", "Champion", 
        "Dynamic", "Elegant", "Energy", "Fantastic", "Gigantic", "Hotel", "Identical", "International", "Contact", "Cozy", 
        "Creative", "Lift", "Magnetic", "Museum", "Nation", "Normal", "Optimal", "Original", "Passion", "Perfect", 
        "Plastic", "Rapid", "Reform", "Sensitive", "Chocolate", "Stable", "Talent", "Theater", "Tradition", "Typical", 
        "University", "Vitamin", "Xylophone", "Yoga", "Zoo", "Zone"
        ]
        # spanish cognates
        spanishCognates = ["Animal", "Artista", "Banana", "Base", "Brillante", "Central", "Campeón", "Clásico", "Comedia", "Creativo",
        "Dinámico", "Energía", "Extraordinario", "Final", "Flexible", "Generación", "Genial", "Hospitalidad", "Ideal", "Imaginación",
        "Innovación", "Journal", "Legítimo", "Local", "Lógico", "Metal", "Música", "Normal", "Optimista", "Original",
        "Passión", "Piano", "Preciso", "Presente", "Rápido", "Relevante", "Selección", "Deporte", "Estable", "Tabla", "Técnico",
        "Tradición", "Universal", "Vacación", "Vibrante", "Vital", "Xilófono", "Yoga", "Zona"
        ]
        # english translations
        translatedSpanishCognates = ["Animal", "Artist", "Banana", "Base", "Brilliant", "Central", "Champion", "Classic", "Comedy", "Creative",
        "Dynamic", "Energy", "Extraordinary", "Final", "Flexible", "Generation", "Great", "Hospitality", "Ideal", "Imagination",
        "Innovation", "Journal", "Legitimate", "Local", "Logical", "Metal", "Music", "Normal", "Optimistic", "Original",
        "Passion", "Piano", "Precise", "Present", "Rapid", "Relevant", "Selection", "Sporty", "Stable", "Table", "Technical",
        "Tradition", "Universal", "Vacation", "Vibrant", "Vital", "Xylophone", "Yoga", "Zone"
        ]
        # french cognates
        frenchCognates = ["Animal", "Artiste", "Banane", "Base", "Brillant", "Central", "Champion", "Classique", "Comédie", "Créatif",
        "Dynamique", "Énergie", "Extraordinaire", "Final", "Flexible", "Génération", "Génial", "Hospitalité", "Idéal", "Imagination",
        "Innovation", "Journal", "Légitime", "Local", "Logique", "Métal", "Musique", "Normal", "Optimiste", "Original",
        "Passion", "Piano", "Précis", "Présent", "Rapid", "Relevant", "Sélection", "Sportif", "Stable", "Table", "Technique",
        "Tradition", "Universel", "Vacance", "Vibrant", "Vital", "Xylophone", "Yoga", "Zone"
        ]
        # english translations
        translatedFrenchCognates = ["Animal", "Artist", "Banana", "Base", "Brilliant", "Central", "Champion", "Classic", "Comedy", "Creative",
        "Dynamic", "Energy", "Extraordinary", "Final", "Flexible", "Generation", "Great", "Hospitality", "Ideal", "Imagination",
        "Innovation", "Journal", "Legitimate", "Local", "Logical", "Metal", "Music", "Normal", "Optimistic", "Original",
        "Passion", "Piano", "Precise", "Present", "Rapid", "Relevant", "Selection", "Sporty", "Stable", "Table", "Technical",
        "Tradition", "Universal", "Vacation", "Vibrant", "Vital", "Xylophone", "Yoga", "Zone"
        ]
        randCognate = ""
        randTranslation = ""
        # get a random number to pull the cognate
        index = random.randint(0,len(translatedNorwegianCognates) - 1)
        # select the correct list based on the current language
        if self.lang == "Norwegian":
            randCognate = norwegianCognates[index]
            randTranslation = translatedNorwegianCognates[index]
        elif self.lang == "Spanish":
            randCognate = spanishCognates[index]
            randTranslation = translatedSpanishCognates[index]
        elif self.lang == "French":
            randCognate = frenchCognates[index]
            randTranslation = translatedFrenchCognates[index]
        # add to output
        self.addToAIOutput(f"A random congnate in {self.lang} is {randCognate}, it means {randTranslation} in English")
        self.setLastResponse("")

    # used to add output to the AI area and allign it vertically
    def addToAIOutput(self, text):        
        self.AIOutputArea.setText(self.AIOutputArea.toPlainText() + '\n\n\n' + '> ' + text)
        self.setVert()
    
    # allign the text box vertically
    def setVert(self):
        # self.AIOutputArea.verticalScrollBar().setValue(self.AIOutputArea.verticalScrollBar().maximum())
        # self.AIOutputArea.verticalScrollBar.setValue(100)
        pass

    # set the last response
    def setLastResponse(self, text):
        self.lastResponse = text

    # choose which LLM call to make
    def handlePrompt(self):
        # if you are in a conversation this will set the system mode to account for this
        if self.HaveAConvoButton.isChecked():
            self.sysMode = 2
        # get the AI output
        self.UserInputArea.setPlainText("")
        text = self.UserInputArea.toPlainText()
        # this is for commands (remove this)
        if text[0] == '/' and self.sysMode == 0:
            if text[0] == '/':
                self.addToAIOutput(LLM.commandCall(text[1:], self.lang, self.lastResponse, self.llm))
                self.setLastResponse("")
                self.handleHistory()
        # this is for defining a word
        elif self.sysMode == 1:
            # word taco is for splitting things easier
            str = "taco " + text
            words = str.split(" ")
            # call the llm
            self.addToAIOutput(LLM.callLLM(5, words, self.lang, None, self.llm))
            # reset system
            self.sysMode = 0
            self.setLastResponse("")
            self.handleHistory()
        # chat mode
        elif self.sysMode == 2:
            # update the chat history
            self.chatHistory += text
            # call the llm
            str = LLM.callLLM(2, text, self.lang, self.chatHistory, self.llm)
            self.addToAIOutput(str)
            # update chat history with the response
            self.chatHistory += str
            self.setLastResponse(str)
        # just a general question catch all
        else:
            # call the llm
            self.addToAIOutput(LLM.callLLM(6, text, self.lang, None, self.llm))
            # reset system
            self.sysMode = 0
            self.setLastResponse("")
            self.handleHistory()
        # reset prompt area

    # determine if the user needs to select a language first
    def selectFirst(self):
        if self.lang != None:
            return True
        self.addToAIOutput("Please select a language first")
        return False
    
    # reset chatHistory and uncheck the conversation button
    def handleHistory(self):
        self.chatHistory = ""
        self.HaveAConvoButton.setChecked(False)

# initiate everything
if __name__ == '__main__':
    app = QApplication(sys.argv)
    options = QStyleFactory.keys()
    app.setStyle(QStyleFactory.create(options[2]))
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())