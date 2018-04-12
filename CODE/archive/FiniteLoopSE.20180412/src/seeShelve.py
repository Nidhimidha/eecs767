#!/usr/bin/python
import shelve
import os

outDir = 'OUTPUT'

files = []
for i in os.listdir(outDir):
        if i.endswith('.db'):
                files.append(os.path.join(outDir, i))

for i in range(len(files)):
        ingest = shelve.open(files[i])
        print "##----------------------------------------------------------##"
        print "Contents of ", files[i]
        for x in ingest:
                print x
                "---------------------"
                print ingest[x]
                print
        ingest.close()
