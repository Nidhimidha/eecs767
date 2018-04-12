import shelve
import os

outDir = 'OUTPUT'

files = []
for i in os.listdir(outDir):
        if i.endswith('.db'):
                files.append(os.path.join(outDir, i))

for i in range(len(files)):
        try:
                ingest = shelve.open(files[i])
        except:
                x = files[i].replace('.db','')
                ingest = shelve.open(x)
                pass
        print ("##----------------------------------------------------------##")
        print ("Contents of ", files[i])
        for x in ingest:
                print(x)
                print("---------------------")
                print(ingest[x])
                print()
        ingest.close()
