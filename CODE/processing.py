import shelve                   ## For generating datastructure db files
from math import log10, sqrt    ## Doing a little math...
import time                     ## For Timing
from functools import wraps     ## For Timing

##-------------------------------------------------------------------------##
## Processing Component of Search Engine Space (follows ingest - preceeds
## Query execution
##-------------------------------------------------------------------------##
## Expects two data structures from an ingest file, a term index and
## document key:
##  index = [ 
##      { 'term': '/A-Za-z0-9/*', 'tfs': [ /0-9/*, ..., /0-9/* ] },
##      ...,
##      { 'term': '/A-Za-z0-9/*', 'tfs': [ /0-9/*, ..., /0-9/* ] },
##  doc_key = [
##      { 'name': '/A-Za-z0-9/*', 'path': '/A-Za-z0-9/* },
##      ...,
##      { 'name': '/A-Za-z0-9/*', 'path': '/A-Za-z0-9/* },
##-------------------------------------------------------------------------##

##-------------------------------------------------------------------------##
## TIMING - DIAGNOSTICS
##-------------------------------------------------------------------------##
## A decorator function to time the execution
##-------------------------------------------------------------------------##
def timing(f):
        @wraps(f)
        def ft(*args, **kwargs):
                t0 = time.time()
                exe = f(*args, **kwargs)
                t1 = time.time()
                print ("\t%s Execution Time (sec): %s" %
                        (f.__name__, str(t1-t0)))
                return exe
        return ft

##-------------------------------------------------------------------------##
## TERM LINKED LIST CLASSES
##-------------------------------------------------------------------------##
## Di : T1 -> T2 -> ... -> Tn
##-------------------------------------------------------------------------##
## A simple one-way linked list node for terms
class TermNode:
    ## Initialize the node
    def __init__(self, term, df, idf, weight):
        self.term = term
        self.df = df
        self.idf = idf
        self.weight = weight
        self.next = None

    ## Get the linked node (next)
    def getNext(self):
        return self.next

    ## Add a node
    def setNext(self, node):
        self.next = node

    ## Print node
    def printNode(self):
        print("\t", "term:", self.term, "weight:", self.weight)

## Document VSM Linked List of Terms
class DocLL:
    ## Initialize the head
    def __init__(self, docID, docName, path):
        self.head = None
        self.docID = docID
        self.docName = docName
        self.path = path
        self.weight = 0
        self.count = 0

    ## Add a node to the list
    def add(self,term, df, idf, weight):
        node = TermNode(term, df, idf, weight)
        node.setNext(self.head)
        self.head = node
        self.count += 1
    
    ## Search for a specific node in the list
    ## Returns node
    def search(self, term):
        cur = self.head
        found = False
        while cur != None and not found:
            if cur.getTerm() == term:
                found = True
            else:
                cur = cur.getNext()
        return cur
    
    ## Remove a node from the list
    def remove(self,term):
        cur = self.head
        prev = None
        found = False
        while not found and cur != None:
            if cur.getTerm() == term:
                found = True
            else:
                prev = cur
                cur = cur.getNext()
        if prev == None:
            self.head = cur.getNext()
            self.count -= 1
        else:
            prev.setNext(cur.getNext())
            self.count -= 1

    ## Print list
    def printList(self):
        print("docID:", self.docID, "docName:", self.docName, 
            "path:", self.path, "weight:", self.weight, "count:", self.count)
        if self.count > 0:
            cur = self.head
            while cur != None:
                cur.printNode()
                cur = cur.getNext()

##-------------------------------------------------------------------------##
##-------------------------------------------------------------------------##
## Generating the Vector Space Model
##-------------------------------------------------------------------------##
##-------------------------------------------------------------------------##

##-------------------------------------------------------------------------##
## Class method to generate VSM Linked List (Doc: T1 -> T2 -> ... -> Tn 
##-------------------------------------------------------------------------##
class genVSMDLL:
    ## Initialize the object
    #@timing ## Uncomment to see discrete timing
    def __init__(self, inFile):
        ## Pull in the data struct(s) from ingest
        ingest = shelve.open(inFile)
        self.index = ingest['index']
        self.doc_key = ingest['doc_key']
        ingest.close()

        ## Sort the index
        self.index.sort(key=lambda k: k['term'])

        ## Initialize linked list array using the doc_key
        self.docVector = [] 
        for x in range(len(self.doc_key)):
            self.docVector.append(DocLL(x, self.doc_key[x]['name'], 
                self.doc_key[x]['path']))


    ## Create the tf-idf weight
    #@timing ## Uncomment to see discrete timing
    def genTFIDF(self):
        ## Loop through the index and make it happen
        for i in range(len(self.index)):
            # Count non-zero indices in arrays
            df = len(list(filter(None,self.index[i]['tfs'])))
            
            # Calculate idf: log(n/df), where n is length
            # of array (# of docs)
            idf = log10(len(self.index[i]['tfs']) / float(df))
            
            # Calculate tf-idf weights (not normalized)
            # |Wi| = sqrt(sum(squared(idf)))
            weights = self.index[i]['tfs']
            w = [float("{0:.3f}".format(sqrt(x*(idf**2)))) for x in weights]
            
            ## Add the term node to the documents
            # Loop through weights per doc and add this term/node to docVector
            for x in range(len(w)):
                self.docVector[x].add(self.index[i]['term'], df, idf, w[x])

            
            # calculate the square of each weight (by doc)
            # and accumulate for doc length
            l = [float("{0:.3f}".format(x**2)) for x in w]
            for x in range(len(self.docVector)):
                self.docVector[x].weight += l[x]

        ## Go through and finish the document weight dot product calculation
        ## Finish the sqrt function
        for x in range(len(self.docVector)):
            self.docVector[x].weight = float("{0:.3f}".format(
                sqrt(self.docVector[x].weight)))

    ## Normalize the vectors using the document weight - have to see if makes
    ## sense here on to perform during query...
    #@timing ## Uncomment to see discrete timing
    def normalizeVectors(self):
            ## For every document in the library (docVector)
            for x in range(len(self.docVector)):
                # Normalize all of the terms
                cur = self.docVector[x].head
                while cur != None:
                    cur.weight = cur.weight / self.docVector[x].weight
                    cur = cur.getNext()

    #@timing ## Uncomment to see discrete timing
    def writeOutput(self, outFile):
        ## Write the Document Vector Space Model (docVector) and
        ## the Document Keystone (doc_key) out to the output file
        out = shelve.open(outFile)
        out['docVector'] = self.docVector
        out['doc_key'] = self.doc_key
        out.close()



##-------------------------------------------------------------------------##
## Class method to generate VSM via array
##-------------------------------------------------------------------------##
class genVSMArray:
        ## Initiliaze the object
        ## Sorts the index
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
                self.docLength = [0]*len(self.index[0]['tfs'])
                
                ## Initialize docVector Array (for storing VSM)
                self.docVector = [ [0]*len(self.index) for _ in range(len(self.doc_key)) ]
            
        ## Create tf-idf weight
        #@timing ## Uncomment to see discrete timing
        def genTFIDF(self):
                ## - First create the df for each term
                ## Loop through index and construct Vector Space Model
                for i in range(len(self.index)):
                        # count non-zero indices in arrays
                        df = len(list(filter(None,self.index[i]['tfs'])))

                        # Calculate idf: log(n/df), where n is length 
                        # of array (# of docs)
                        idf = log10(len(self.index[i]['tfs']) / float(df))

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
                        l = [float("{0:.3f}".format(x**2)) 
                                for x in w]
                        for x in range(len(self.docLength)):
                            self.docLength[x] += l[x]

                        # Place in dictionary (for now)
                        self.index[i]['df'] = df
                        self.index[i]['idf'] = "{0:.3f}".format(idf)
                        self.index[i]['w'] = w

        ## Normalize the vectors using docLength - establish unit vectors
        #@timing ## Uncomment to see discrete timing
        def normalizeVectors(self):
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

##-----------------------------------------------------------------##
## Function based method for generating VSM array
##-----------------------------------------------------------------##
## First pass, brute force method
##-----------------------------------------------------------------##
#@timing ## Uncomment to see discrete timing
def brute_force():
        ## GET THE DATA FROM INGEST
        ingest = shelve.open('OUTPUT/ingestOutput.db')
        index = ingest['index']
        doc_key = ingest['doc_key']
        ingest.close()

        ## First sort the index
        index.sort(key=lambda k: k['term'])

        ## Initialize docLength Array (for normalizing weights)
        docLength = [0]*len(index[0]['tfs'])
                
        ## Initialize docVector Array (for storing VSM)
        docVector = [[0]*len(index) for _ in range(len(doc_key))]

        ## Create tf-idf weight
        ## - First create the df for each term
        ## Loop through index and construct Vector Space Model
        for i in range(len(index)):
                # Count non-zero indices in arrays
                df = len(list(filter(None,self.index[i]['tfs'])))

                # Calculate idf: log(n/df), where n is length of array 
                # (# of docs)
                idf = log10(len(index[i]['tfs']) / float(df))

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
                l = [float("{0:.3f}".format(x**2)) for x in w]
                for x in range(len(self.docLength)):
                    self.docLength[x] += l[x]
        
                # Place in dictionary (for now)
                index[i]['df'] = df 
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
## Our 'MAIN' method - fun fun... ;)
##-----------------------------------------------------------------##
@timing
def main():
        ## Execution as an object - result is VSM Doc LL
#        dLLVSM = genVSMDLL('OUTPUT/ingestOutput.db')
#        dLLVSM.genTFIDF()
#        dLLVSM.normalizeVectors()
#        dLLVSM.writeOutput('OUTPUT/processingOutput')

        ## Execution as an object - result is VSM array
        simpleVSM = genVSMArray('OUTPUT/ingestOutput')
        simpleVSM.genTFIDF()
        simpleVSM.normalizeVectors()
        simpleVSM.writeOutput('OUTPUT/processingOutput')

        ## Execution as a pure function
#       brute_force()

##-----------------------------------------------------------------##
## Execute the main... pretending to be C :)
##-----------------------------------------------------------------##
if __name__ == "__main__":
        main()
