import shelve
from math import log10, sqrt
import numpy as np

## Brute Force first...

## GET THE DATA FROM INGEST
ingest = shelve.open('OUTPUT/ingestOutput.db')
index = ingest['index']
doc_key = ingest['doc_key']
ingest.close()

##----- BEGIN DEBUG ------##
#print "DOCUMENT LIBRARY"
#for i in range(len(doc_key)):
#	print doc_key[i]
##----- END DEBUG ------##

## First sort the index
index.sort(key=lambda k: k['term'])

## Array for storing the docLength (for normalizing
docLength = np.array([0]*len(index[0]['tfs']))

## Array for storing doc VSM
docVector = np.zeros(shape=(len(doc_key),len(index)))

##----- BEGIN DEBUG ------##
#print "TF-IDF - NOT NORMALIZED"
##----- END DEBUG ------##

## Create tf-idf weight
## - First create the df for each term
## Loop through index and construct Vector Space Model
for i in range(len(index)):
	# Use numpy array to count non-zero indices in arrays
	df = (np.array([index[i]['tfs']]) != 0).sum(1)

	# Calculate idf: log(n/df), where n is length of array (# of docs)
	idf = log10(len(index[i]['tfs']) / float(df[0]))

	# Calculate tf-idf weights (not normalized)
	# |Wi| = sqrt(sum(squared(idf)))
	weights = index[i]['tfs']
	w = [float("{0:.3f}".format(sqrt(x*(idf**2)))) for x in weights]
	
	# Loop through weights per doc and add to docVector
	for x in range(len(w)):
		docVector[x][i] = w[x]
 
	# calculate the square of each weight (by doc) and accumulate for
	# doc length
	l = np.array([float("{0:.3f}".format(x**2)) for x in w])
	docLength = docLength + l
	
	# Place in dictionary (for now)
	index[i]['df'] = df[0] 
	index[i]['idf'] = "{0:.3f}".format(idf) # Round to three digits
	index[i]['w'] = w
	
	##----- BEGIN DEBUG ------##
	#print index[i]['term'], index[i]['w']
	##----- END DEBUG ------##

## Now finish length of Di (docLength)
docLength = [float("{0:.3f}".format(sqrt(x))) for x in docLength]

##----- BEGIN DEBUG ------##
#print index[i]['term'], index[i]['w']
#print "DOCUMENT LENGTHS"
#print docLength
##----- END DEBUG ------##

## Normalize the Document Vector Space Model
for x in range(len(docVector)):
	for y in range(len(docVector[x])):
		docVector[x][y] /= docLength[x]
		docVector[x][y] = float("{0:.3f}".format(docVector[x][y])) 

##----- BEGIN DEBUG ------##
#print "Document Vector Space Model"
#print docVector
##----- END DEBUG ------##

## Write the Document Vector Space Model (docVector) and
## the Document Keystone (doc_key) out to the output file
out = shelve.open('OUTPUT/processingOutput')
out['docVector'] = docVector
out['doc_key'] = doc_key
out.close()



