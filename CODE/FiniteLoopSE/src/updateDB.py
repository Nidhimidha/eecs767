import shelve
import sys

old = 'download_manifest'
new = 'download_manifest-1'

if(len(sys.argv)>1):
        old = sys.argv[1]
if(len(sys.argv)>2):
        new = sys.argv[2]

if(len(sys.argv)<2):
        print("Usage: python3 updateDB.py <old shelve>")
        print("      - to read a db file")
        print("Usage: python3 updateDB.py <old shelve> <new shelve>")
        print("      - to create a new db file from the old")
        print()
        quit()

print('Opening:', old)

data = {}

olddb = shelve.open(old)
keys = list(olddb.keys())
for k in keys:
        data[k] = olddb[k]
olddb.close()

if(len(sys.argv) == 2):
        print(data)
else:
        print('Found:', keys)

if(len(sys.argv) == 3):
        print('Creating:', new)

        newdb = shelve.open(new)
        for k in keys:
                newdb[k] = data[k]
        newdb.close()

        print('New file created')




#blah = shelve.open('/home/terrapin/EECS767/cached_docs/download_manifest')
#print('WTF')
#keys = list(blah.keys())
#t = blah['manifest']
#print(blah['manifest'])
#blah.close()

#x = shelve.open('download.db')
#x['manifest'] = t
#x.close()

#y = shelve.open('download.db')
#print(y['manifest'])
#y.close()
