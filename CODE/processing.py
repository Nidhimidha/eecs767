import shelve			## For generating datastructure db files
from math import log10, sqrt	## Doing a little math...
import numpy as np		## Using numpy arrays for optimized manipulation
import time			## For Timing
from functools import wraps	## For Timing

## A decorator function to time the execution
def timing(f):
	@wraps(f)
	def ft(*args, **kwargs):
		t0 = time.time()
		exe = f(*args, **kwargs)
		t1 = time.time()
		print ("\t%s Execution Time (sec): %s" %
			(f.func_name, str(t1-t0)))
		return exe
	return ft

## A simple one-way linked list
## A node in the list
class Node:
    ## Initialize the node
    def __init__(self, dName):
        self.name = dName
        self.next = None

    ## Get the name parameter - the document name
    def getName(self):
        return self.name
    
    ## Get the linked node (next)
    def getNext(self):
        return self.next

    ## Add a node
    def setNext(self,n):
        self.next = n

## The actual linked list
class linkedList:
    ## Initialize the head
    def __init__(self):
        self.head = None

    ## Check if list is empyt
    def isEmpty(self):
        return self.head == None

    ## Add a node to the list
    def add(self,n):
        node = Node(n)
        node.setNext(self.head)
        self.head = node
    
    ## Returns the size of the list
    ## Checks current linked list - in lieu of just tracking it...
    def size(self):
        cur = self.head
        count = 0
        while cur != None:
            count += 1
            cur = cur.getNext()
        return count
    
    ## Search for a specific node in the list
    def search(self, name):
        cur = self.head
        found = False
        while cur != None and not found:
            if cur.getName() == name:
                found = True
            else:
                cur = cur.getNext()
        return found
    
    ## Remove a node from the list
    def remove(self,name):
        cur = self.head
        prev = None
        found = False
        while not found:
            if cur.getData() == name:
                found = True
            else:
                prev = cur
                cur = cur.getNext()
        if prev == None:
            self.head = cur.getNext()
        else:
            prev.setNext(cur.getNext())


## The crux of this script - generating the Vector Space Model
class genVSM:
	## Initiliaze the object
	#@timing ## Uncomment to see discrete timing
	def __init__(self, inFile):
		## Pull in the data structure(s) from ingest
		ingest = shelve.open(inFile)
		self.index = ingest['index']
		self.doc_key = ingest['doc_key']
		ingest.close()

		## Sort the index
		self.index.sort(key=lambda k: k['term'])

		## Initialize docLength Array (for normalizing weights)
		self.docLength = np.array([0]*len(self.index[0]['tfs']))
		
		## Initialize docVector Array (for storing VSM)
		self.docVector = np.zeros(shape=(len(self.doc_key),
			len(self.index)))

        ## Create tf-idf weight
	#@timing ## Uncomment to see discrete timing
	def genTFIDF(self):
		## - First create the df for each term
		## Loop through index and construct Vector Space Model
		for i in range(len(self.index)):
			# Use numpy array to count non-zero indices in arrays
			df = (np.array([self.index[i]['tfs']]) != 0).sum(1)

			# Calculate idf: log(n/df), where n is length 
			# of array (# of docs)
			idf = log10(len(self.index[i]['tfs']) / float(df[0]))

			# Calculate tf-idf weights (not normalized)
			# |Wi| = sqrt(sum(squared(idf)))
			weights = self.index[i]['tfs']
			w = [float("{0:.3f}".format(sqrt(x*(idf**2)))) 
				for x in weights]

			# Loop through weights per doc and add to docVector
			for x in range(len(w)):
				self.docVector[x][i] = w[x]

			# calculate the square of each weight (by doc) 
			# and accumulate for doc length
			l = np.array([float("{0:.3f}".format(x**2)) 
				for x in w])
			self.docLength = self.docLength + l

			# Place in dictionary (for now)
			self.index[i]['df'] = df[0]
			self.index[i]['idf'] = "{0:.3f}".format(idf)
			self.index[i]['w'] = w

	## Normalize the vectors using docLength - establish unit vectors
	#@timing ## Uncomment to see discrete timing
	def normalizeVector(self):
		## Now finish length of Di (docLength)
		self.docLength = [float("{0:.3f}".format(sqrt(x))) 
			for x in self.docLength]

		## Normalize the Document Vector Space Model
		for x in range(len(self.docVector)):
			for y in range(len(self.docVector[x])):
				self.docVector[x][y] /= self.docLength[x]
				self.docVector[x][y] = float("{0:.3f}".format(
					self.docVector[x][y]))

	#@timing ## Uncomment to see discrete timing
	def writeOutput(self, outFile):
		## Write the Document Vector Space Model (docVector) and
		## the Document Keystone (doc_key) out to the output file
		out = shelve.open(outFile)
		out['docVector'] = self.docVector
		out['doc_key'] = self.doc_key
		out.close()

	## For debug
	def printObject(self, obj):
		print(obj)



## Initial Solution space as a function 
#@timing ## Uncomment to see discrete timing
def brute_force():
	## GET THE DATA FROM INGEST
	ingest = shelve.open('OUTPUT/ingestOutput.db')
	index = ingest['index']
	doc_key = ingest['doc_key']
	ingest.close()

	## First sort the index
	index.sort(key=lambda k: k['term'])

	## Array for storing the docLength (for normalizing
	docLength = np.array([0]*len(index[0]['tfs']))

	## Array for storing doc VSM
	docVector = np.zeros(shape=(len(doc_key),len(index)))

	## Create tf-idf weight
	## - First create the df for each term
	## Loop through index and construct Vector Space Model
	for i in range(len(index)):
		# Use numpy array to count non-zero indices in arrays
		df = (np.array([index[i]['tfs']]) != 0).sum(1)

		# Calculate idf: log(n/df), where n is length of array 
		# (# of docs)
		idf = log10(len(index[i]['tfs']) / float(df[0]))

		# Calculate tf-idf weights (not normalized)
		# |Wi| = sqrt(sum(squared(idf)))
		weights = index[i]['tfs']
		w = [float("{0:.3f}".format(sqrt(x*(idf**2)))) 
			for x in weights]
	
		# Loop through weights per doc and add to docVector
		for x in range(len(w)):
			docVector[x][i] = w[x]
 
		# calculate the square of each weight (by doc) and 
		# accumulate for
		# doc length
		l = np.array([float("{0:.3f}".format(x**2)) for x in w])
		docLength = docLength + l
	
		# Place in dictionary (for now)
		index[i]['df'] = df[0] 
		index[i]['idf'] = "{0:.3f}".format(idf) # Round to three digits
		index[i]['w'] = w
	
	## Now finish length of Di (docLength)
	docLength = [float("{0:.3f}".format(sqrt(x))) for x in docLength]

	## Normalize the Document Vector Space Model
	for x in range(len(docVector)):
		for y in range(len(docVector[x])):
			docVector[x][y] /= docLength[x]
			docVector[x][y] = float("{0:.3f}".format(
				docVector[x][y])) 

##-----------------------------------------------------------------##
## For now....
## Execution from here
##-----------------------------------------------------------------##

@timing
def main():
	## Execution as an object
	simpleVSM = genVSM('OUTPUT/ingestOutput.db')
	simpleVSM.genTFIDF()
	simpleVSM.normalizeVector()
	simpleVSM.writeOutput('OUTPUT/processingOutput')
	#simpleVSM.printObject(simpleVSM.docVector)

	## Execution as a pure function
	#brute_force()

if __name__ == "__main__":
	main()
