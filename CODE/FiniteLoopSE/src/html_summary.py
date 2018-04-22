#!/usr/bin/python3

##
##
## Takes waaay too long, even for just 10 files (7 secs)
##
## Need to read in the processingOutput.db
## To make it easy to find .... a dictionary of documents containing
## a dictionary of terms which leads to the text
##
## Hopefully won't be too slow...
##
##
from os import listdir, rename
from os.path import isfile, join
import re
from random import randint
import shelve
import time
import sys

print("Parsing HTML Files")

inFile = 'OUTPUT/processingOutput.db'
outFile = 'OUTPUT/htmlData'
path = 'INPUT/control'
htmlText = {}

## Since things can change - let's check to see if we were called as:
## html_summary.py <cache path> <processOutput.db>
if(len(sys.argv)>1):
        path = sys.argv[1]
if(len(sys.argv)>2):
        inFile = sys.argv[2]

edge = 4        # Number of words on either side of term to retrieve

t0 = time.time()        # timing

## Need to read the processingOutput files to get all of the keys
print("\tIngesting", inFile)
try:
        ingest = shelve.open(inFile)
except:
        x = inFile.replace('.db', '')
        ingest = shelve.open(x)
        pass

## Need to suck in the list of terms from processingOutput::termIndex
query = list(ingest['termIndex'].keys())

## Need to get the document list from processingOutput::doc_key
## [ {doc name: [doc id, doc path, url]
## Unfortunately, the doc path is unique to where the crawler was run
## Grab the file name and join with path variable
doc_key = ingest['doc_key']
docList = []
for x in doc_key:
        docList.append(list(x.keys())[0])

## Close the ingest file
ingest.close()

## This goes through the path directory outright - let's use the docList
#files = [ x for x in listdir(path) if isfile(join(path, x))]
## Let's use this to make sure we have valide files to work on
files = [ x for x in docList if isfile(join(path, x)) ]

## Go through each document - we're going to do this the painful way
## then go through each term and search
for c in range(len(files)):
        ## Initialize htmlText for this document
        htmlText[files[c]] = {}

        print("Looking at", join(path, files[c]))

        ## Read in the file and clean it up        
        F = open(join(path, files[c]), 'r')
        words = F.read()
        F.close()

        ## First kill everything up to <BODY> or <body>
        words = re.sub('\s+',' ', words)
        words = re.sub('^.*<body .*?>', '', words, flags=re.I)
        words = re.sub('</body.*$', '', words, flags=re.I)
        words = re.sub('<.*?>', '', words)
        words = re.sub('\s+',' ', words)

        ## Now look for all of the terms from the termIndex
        for y in range(len(query)):
                print("\tSearching for: ", query[y])

                ## See if we can find it
                match = '\w*\W*' * edge + query[y] + '\W*\w*' * edge
                found = re.findall(match, words, re.I)

                ## If we found the text, add it to the htmlText
                if len(found) > 0:
                        ## Pick a random entry
                        i = randint(0, len(found)-1)

                        ## Add it the dictionary
                        htmlText[files[c]][query[y]] = found[i]


## Save the datastructure to our own db file
print("\tWriting output file: ", outFile)
out = shelve.open(outFile)
out['htmlText'] = htmlText
out.close()

## Let's see if the shelve produced a .db file or not, if not - fix it
if isfile(outFile):
        ## Does not end in .db...
        rename(outFile, outFile+'.db')

t1 = time.time()

print("Execution Time (sec): %s" % str(t1-t0))

#        print("\tApplying bold")
#        ## Make all of the query piece bold
#        ## This will need to be done in search.cgi on the final listing
#        for y in range(len(query)):
#                bold = '<b>'+query[y]+'</b>'
#                summary = re.sub(str(query[y]), str(bold), summary, flags=re.I)
#
#       print('\t\t', summary)


