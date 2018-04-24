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
from nltk.corpus import stopwords
#import threading

print("Parsing HTML Files")

inFile = 'OUTPUT/processingOutput.db'
outDir = 'OUTPUT/CACHE'
path = 'INPUT/cached_docs'
offset = 1
countpp = 10    # Count per process

## Since things can change - let's check to see if we were called as:
## html_summary.py <input path> <processOutput.db> <offset>
if(len(sys.argv)>1):
        path = sys.argv[1]
if(len(sys.argv)>2):
        inFile = sys.argv[2]
## Offset is to determine which set we are in
## The number of sets is determined by the number of files / count per process
if(len(sys.argv)>3):
        offset = sys.argv[3]

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

## Let's use the nltk stop words to prune this a bit
nonwords = stopwords.words('english')
stop = {}
## Make it a dictionary for lookup
for n in nonwords:
        stop[n] = ''

## Need to suck in the list of terms from processingOutput::termIndex
## Too slow
#query = list(ingest['termIndex'].keys())
## Get list from document itself

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

def parseMe(filename):
        htmlText = {}

        ## Initialize htmlText for this document
        #htmlText[files[c]] = {}
        htmlText[filename] = {}

        #print("Looking at", join(path, files[c]))
        print("Looking at", join(path, filename))

        ## Read in the file and clean it up        
        #F = open(join(path, files[c]), 'r')
        F = open(join(path, filename), 'r')
        words = F.read()
        F.close()

        ## First kill everything up to <BODY> or <body>
        words = re.sub('\s+',' ', words)
        words = re.sub('^.*<body .*?>', '', words, flags=re.I)
        words = re.sub('</body.*$', '', words, flags=re.I)
        ## May need to do the same for <script to /script> tags
        # words = re.sub('<script.*?/script>', '', words, flags=re.I)
        words = re.sub('<.*?>', '', words)
        words = re.sub('\s+',' ', words)
        words = re.sub('&nbsp;', ' ', words, flags=re.I)
        words = re.sub('[)(\*&\\/=>"\',\.:;@#]', ' ', words)

        ## Create the query list based on the terms in the document
        terms = {}
        for t in words.split():
                t = re.sub('\W', '', t)
                ## If a stopword, blank it out
                if t in stop:
                        t = ''
                if t != '':
                        terms[t.lower()] = ''
        query = list(terms.keys())

        ## Now look for all of the terms from the termIndex
        for y in range(len(query)):
                print("\tSearching for: ", query[y])

                ## See if we can find it
                match = '\w*\W*' * edge + query[y] + '\W*\w*' * edge
                #found = re.findall(match, words, re.I)
                m = re.search(match, words, re.IGNORECASE)
                result = m.group(0) if m else ""

                ## If we found the text, add it to the htmlText
                #if len(found) > 0:
                        ## Pick a random entry
                #        i = randint(0, len(found)-1)

                        ## Add it the dictionary
                        #htmlText[filename][query[y]] = found[i]
                htmlText[filename][query[y]] = result
        ## Now write out the cache file to the outDir using the filename
        ## of the original doc as the database filename
        #print("\tWriting output file", files[c]+'.db', 'to', outDir)
        print("\tWriting output file", filename+'.db', 'to', outDir)
        #out = shelve.open(join(outDir, files[c]))
        out = shelve.open(join(outDir, filename))
        out['htmlText'] = htmlText
        out.close()
        ## Reset htmlText for next document
        #htmlText = {}

        ## Make sure we have a .db file
        #if isfile(join(outDir, files[c])):
        if isfile(join(outDir, filename)):
                ## Does not end in .db....
                #rename(join(outDir, files[c]), join(outDir, files[c]+'.db'))
                rename(join(outDir, filename), join(outDir, filename+'.db'))

## Go through each document - we're going to do this the painful way
## then go through each term and search
## Should probably thread this process
## Tried threading - caused the machine to thrash
## Executing in a manual multiprocessor method

## offset - where we want to start
## countpp - how many to run in the calling
batch = len(files) / countpp
bstart = (int(offset)-1) * countpp
bend = bstart + countpp - 1

print("%s Total files -> %s batches with %s files per batch" %
        (len(files), str(len(files)/countpp), countpp))

if bend >= len(files):
        if bstart < len(files):
                bend = len(files) - 1
        else:
                print("There are no batches in this range to work on")
                quit()

print("Working on files %s through %s" % (bstart, bend))

for c in range(len(files)):
        print( "Working on index:", c)
        ## Make sure that we haven't cached this file already
        ftest = join(outDir, files[c]+'.db')
        if isfile(join(outDir, files[c]+'.db')):
                print('Skipping %s, as the file has already been cached' %
                         files[c])
        else:
                st0 = time.time()
                parseMe(files[c])
                st1 = time.time()
                print("Completed processing of %s in %s sec" %
                        (files[c], str(st1-st0)))

t1 = time.time()

print("Total Execution Time (sec): %s" % str(t1-t0))
print("Processed %s files" % len(files))

