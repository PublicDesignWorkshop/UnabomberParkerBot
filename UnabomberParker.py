from twython import Twython, TwythonError
from threading import Timer
from secrets import *
from random import randint

import nltk
from nltk.corpus import PlaintextCorpusReader
from nltk.corpus import cmudict

import curses
from curses.ascii import isdigit

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)


def tweet(tweet):
	"""
	Tweets a string
	"""
	twitter.update_status(status = tweet);


def getCorpus(fileLocation, fileids):
	"""
	Takes in a location of files and  list of fileids and turns
	those files into corpus
	"""
	docs = PlaintextCorpusReader(fileLocation, fileids)

	return docs

d = cmudict.dict()

def countSyllables(word):
	"""
	Returns the amount of syllables in a word
	"""
	try:
		return max([len([y for y in x if isdigit(y[-1])]) for x in d[word.lower()]])
	except:
		return None

def editDoc(docName):
	doc = open(docName, 'r')
	docList = doc.readlines()
	doc.close()

	newLines = []
	for line in docList:
		newLines.append(line.replace('\n', ''))

	doc = open(docName,'w')
	for line in newLines:
		doc.write(line)
	doc.close()

def editDoc2(docName):
	doc = open(docName, 'r')
	docList = doc.readlines()
	doc.close()

	newLines = []
	for line in docList:
		newLines.append(line.replace('\n', ' \n '))

	doc = open(docName,'w')
	for line in newLines:
		doc.write(line)
	doc.close()

def getPoetryList(docName):
    """
    Gets a list of poetry from a document
    """
    doc = open(docName, 'r', encoding = 'utf8')

    docList = doc.readlines()                       #Get list of lines of poetry
    doc.close()


    poetryList = []
    currPoem = ""

    for line in docList:
        line = line.strip('"')
        
        # try:
        #   print(line)
        # except:
        #   print("Can't print!")
        if line != "  \n" and line != " \n" and line != "\n":   #Append lines of poetry
            currPoem = currPoem + line
            # print(line.encode('utf8').decode('utf8'))
            # try:
            #   print(line)
            # except:
            #   print("Can't print!")
        else:                                                   #If its a newline, it's a new poem
            poetryList.append(currPoem)
            # print("New poem!")
            currPoem = ""

    # doc.close()
    return poetryList[1:]


def makeNewTweet(corpus, poetryList, doc2):
    """
    Reinvents a sentence from a poem by feeding words from doc2 into it
    """

    # sentences1 = corpus.sents(doc1)
    sentences2 = corpus.sents(doc2)             #Sentences from second document

    sent1orig = poetryList[randint(0, len(poetryList)-1)].encode('utf8').decode('utf8').split(" ")
    sent1 = []                                  #Get random poem
    for word in sent1orig:                      #Make list of words from poem, separating punctuation
        if word != "" and word[-1] in ",.:;":
            sent1.append(word[:-1])
            sent1.append(word[-1])
        elif word != "":
            sent1.append(word)


    sent2 = None
    while(sent2 == None):                       #Get random sentence from doc2
        sent2 = sentences2[randint(0, len(sentences2)-1)]
        if sent2[0].strip("1234567890") == "":  #Check if it's actually a sentence and not numbers.
            sent2 = None

    sents = [sent1, sent2]

    tags = []
    # print(sent1)

    for sent in sents:                          #Get parts-of-speech tags for each word in both sentence/poem
        print('\n')
        tag = nltk.pos_tag(sent)
        tags.append(tag)
        try:
            print(tag)
        except:
            print("Couldn't print!")

    sent1Tags = []                              #A list of pos tags from the poem
    for word in tags[0]:
        sent1Tags.append(word[1])

    # print("\n", sent1Tags)

    numEdits = 0

    nounCounter = 0             #Counters for each pos and how many have already been replaced
    nnsCounter = 0
    vbCounter = 0
    vbdCounter = 0
    vbnCounter = 0
    adjCounter = 0
    newSentence = sent1
    for word in tags[1]:        #for each word in the second document
        posTag = word[1]

        #disregard these words, theyre not worth replacing other words
        disregardWords = ["been", "be", "is", "am", "are", "own", "our", "do", "did", "can", "cannot"]

        if not (word[0].lower() in disregardWords):
            if posTag == 'NNP' or posTag == 'NN':               #If the word is a noun
                # print(word[0])
                count = 0
                tCount = 0
                found = False
                for t in sent1Tags:                             #iterate through the tags in the poem
                    if (t == 'NNP' or t == "NN") and not found: #until another noun is found
                        if count == nounCounter and newSentence[tCount] != "\n" and not newSentence[tCount] in disregardWords:
                            newSentence[tCount] = word[0]       #If this noun hasn't been replaced yet, replace it
                            nounCounter += 1                    #Increase number of nouns edited
                            found = True
                            numEdits += 1                       #Increase number of edits
                        else:                                   #Else if this noun has already been replaced
                            count += 1                          #Say you've hit a replaced noun and move to the next

                    tCount += 1                                 #Increase the index of words being looked at
            elif posTag == "NNS":                               #Repeat the process with all other parts of speech, like plural nouns
                count = 0
                tCount = 0
                found = False
                for t in sent1Tags:
                    if (t == 'NNS') and not found:
                        if count == nnsCounter and newSentence[tCount] != "\n" and not newSentence[tCount] in disregardWords:
                            newSentence[tCount] = word[0]
                            nnsCounter += 1
                            found = True
                            numEdits += 1
                        else:
                            count += 1

                    tCount += 1
            elif posTag == "VB":                                #Verbs
                count = 0
                tCount = 0
                found = False
                for t in sent1Tags:
                    if (t == 'VB') and not found:
                        if count == vbCounter and newSentence[tCount] != "\n" and not newSentence[tCount] in disregardWords:
                            newSentence[tCount] = word[0]
                            vbCounter += 1
                            found = True
                            numEdits += 1
                        else:
                            count += 1

                    tCount += 1
            elif posTag == "VBD":                               #Past tense verbs
                count = 0
                tCount = 0
                found = False
                for t in sent1Tags:
                    if (t == 'VBD') and not found:
                        if count == vbdCounter:
                            newSentence[tCount] = word[0]
                            vbdCounter += 1
                            found = True
                            numEdits += 1
                        else:
                            count += 1

                    tCount += 1
            elif posTag == "VBN":                               #Past participle verbs
                count = 0
                tCount = 0
                found = False
                for t in sent1Tags:
                    if (t == 'VBN') and not found:
                        if count == vbnCounter:
                            newSentence[tCount] = word[0]
                            vbnCounter += 1
                            found = True
                            numEdits += 1
                        else:
                            count += 1

                    tCount += 1
            elif posTag == "JJ":                                #Adjectives
                count = 0
                tCount = 0
                found = False
                for t in sent1Tags:
                    if (t == 'JJ') and not found:
                        if count == adjCounter:
                            newSentence[tCount] = word[0]
                            adjCounter += 1
                            found = True
                            numEdits += 1
                        else:
                            count += 1

                    tCount += 1

    # print("\n", newSentence)



    # sentStrings = []

    # for sent in sents:
    if numEdits == 0:
        print("No changes!")
        return None

    formatSent = ""
    index = 0

    for word in newSentence:                                #Format poem
        if index == 0:
            formatSent = word.capitalize()
        elif word in ".,'!?-:;":
            formatSent = formatSent + word
        elif formatSent[-1:] == "'" and word == 's':
            formatSent = formatSent + word
        elif formatSent[-1:] == "\n":
            formatSent = formatSent + word.capitalize()
        else:
            formatSent = formatSent + " " + word

        index += 1


    # print(formatSent)
    return formatSent

    #   sentString.append(formatSent)



def runBot():
    corpus = getCorpus('Docs', '.*')

    
    poetryList = getPoetryList('dorothy_parker.txt')

    # num = randint(0, len(poetryList)-1)

    # print(str(num))
    # print(poetryList[num])
    found = False
    while not found:                                #Keep trying to find a poem that is good
        newTweet = makeNewTweet(corpus, poetryList, 'unabom.txt')
        if newTweet != None and len(newTweet) <= 140:
            found = True

    try:
        print(newTweet)
    except:
        print("Couldn't Print!")

    if not debug:
        try:
            tweet(newTweet)
            print("I just tweeted!")
        except:
            print("Ran into a problem tweeting!")




def setInterval(func, sec):
    def func_wrapper():
        setInterval(func, sec)
        func()
    t = Timer(sec, func_wrapper)
    t.start()
    return t


debug = True
runOnce = True

runBot()
if not runOnce:
    setInterval(runBot, 60*60*3)        #runs every 3 hours

# editDoc2('Docs\dorothy_parker.txt')
