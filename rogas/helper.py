
'''
This file contains some useful functions

@author: Yan Xiao 
'''

import os

#get the graph from materialised graph dir or tmp graph dir
def getGraph(graphName):
    matGraphDir = os.environ['HOME'] + "/RG_Mat_Graph/"
    tmpGraphDir = "/dev/shm/RG_Tmp_Graph/"
    
    if os.path.exists(tmpGraphDir + graphName):
        return tmpGraphDir + graphName
    elif os.path.exists(matGraphDir + graphName):
        return matGraphDir + graphName
    else:
        raise RuntimeError, "No such graph!!"

#word appears in the begin, end in string, or mid with spaces(\t\n\r\space) around 
def findWordInString(word, sString):
    def isWordBoundary(character):
        return character.isspace() or character in [',', '(', ')', ';']

    searchBeginIndex = 0
    searchEndIndex = len(sString)
    while True:
        wordIndex = sString.find(word, searchBeginIndex, searchEndIndex)
        if wordIndex == -1:
            return -1
        
        if (wordIndex > searchBeginIndex and not isWordBoundary(sString[wordIndex-1])) or (wordIndex + len(word) < searchEndIndex and not isWordBoundary(sString[wordIndex+len(word)])):
            searchBeginIndex = wordIndex + len(word)
        else:
            return wordIndex

def getAlphaNumSubString(word):
    startIndex = 0
    endIndex = 0  
    for index in range(len(word)):
        if word[index].isalnum():
            startIndex = index
            break

    for index in range(len(word)):
        realIndex = len(word) - 1 - index
        if word[realIndex].isalnum():
            endIndex = realIndex 
            break

    return  word[startIndex:endIndex+1]

def subprocessCmd(cmd):
    import subprocess
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
    return pipe.read()

