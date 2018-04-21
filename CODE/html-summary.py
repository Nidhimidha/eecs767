#!/usr/bin/python3

##
##
## Takes waaay too long, even for just 10 files (7 secs)
##
## Need to read in the processingOutput.db
## Create an nxm matrix s.t. n = term and m = doc
## place the summary for each term in (i,j)
##
## Quey will have to suck it in and pick the (i,j) it
## should already know
## Hopefully won't be too slow...
##
##
from os import listdir
from os.path import isfile, join

import re

from random import randint

path = './cached_docs'
query = ['standard', 'profile', 'cost']
edge = 4

files = [ x for x in listdir(path) if isfile(join(path, x))]

for c in range(0, 9):
        summary = ''

        ## Grab a random file for now
        x = randint(0, len(files)-1)

        print("Looking at", join(path, files[x]))
        
        F = open(join(path, files[x]), 'r')
        words = F.read()
        F.close()

        ## First kill everything up to <BODY> or <body>
        words = re.sub('\s+',' ', words)
        words = re.sub('^.*<body .*?>', '', words, flags=re.I)
        words = re.sub('</body.*$', '', words, flags=re.I)
        words = re.sub('<.*?>', '', words)
        words = re.sub('\s+',' ', words)

        ## See if we can find the query terms
        for y in range(len(query)):
                print("\tSearching for: ", query[y])

                ## See if we can find it
                match = '\w*\W*' * edge + query[y] + '\W*\w*' * edge
                found = re.findall(match, words, re.I)

                ## If we found the text, add it
                if len(found) > 0:
                        ## Pick a random entry
                        i = randint(0, len(found)-1)

                        ## Add it to the summary
                        summary += '...' + found[i]

        print("\tApplying bold")
        ## Make all of the query piece bold
        for y in range(len(query)):
                bold = '<b>'+query[y]+'</b>'
                summary = re.sub(str(query[y]), str(bold), summary, flags=re.I)

        print('\t\t', summary)


