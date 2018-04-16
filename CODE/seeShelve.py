#!/usr/bin/python3
import shelve
import os
import sys

outDir = 'OUTPUT'

files = []
for i in os.listdir(outDir):
        if i.endswith('.db'):
                files.append(os.path.join(outDir, i))

if(len(sys.argv)>1):
        files = []
        files.append(sys.argv[1])

for i in range(len(files)):
        ingest = shelve.open(files[i])
        print("##----------------------------------------------------------##")
        print("Contents of ", files[i])
        for x in ingest:
                print(x)
                print("---------------------")
                print(ingest[x])
                print()
        ingest.close()
