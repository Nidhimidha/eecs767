import shelve                   ## For generating datastructure db files
from math import log10, sqrt    ## Doing a little math...
import time                     ## For Timing
from functools import wraps     ## For Timing

inFile = 'OUTPUT/ingestOutput.db'
outFile = 'OUTPUT/processingOutput'

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
## Class method to generate VSM via array
##-------------------------------------------------------------------------##
class genVSMArray:
        ## Initiliaze the object
        ## Sorts the index
        #@timing ## Uncomment to see discrete timing
        def __init__(self, inFile):
                ## Pull in the data structure(s) from ingest
                try:
                        ingest = shelve.open(inFile)
                except:
                        x = inFile.replace('.db','')
                        ingest = shelve.open(x)
                        pass

                self.index = ingest['index']
                self.doc_key = ingest['doc_key']
                self.proximity = ingest['proximity']
                ingest.close()

                ## Sort the index and proximity (need to match)
                ## Need to modify from
                ## { term : [counts], ...
                ## to
                ## [ {term : [counts] }, ...
                #mylist = sorted(self.index.iterkeys())
                self.mylist = [key for key in sorted(self.index.keys())]
                tempIndex = []
                for x in self.mylist:
                        tempIndex.append( { x : self.index[x] } )
                self.index = tempIndex

                #self.index.sort(key=lambda k: k.keys())
                #sorted(self.index.iterkeys())

                ## Initialize docLength Array (for normalizing weights)
                #w = self.index[0].keys()[0]
                #w = self.index.keys()[0]
                w = self.mylist[0]
                self.docLength = [0]*len(self.index[0][w])
                
                ## Need to modify the doc_key from
                ## { doc_name : [doc_id, loc, url], ...
                ## to
                ## [ { doc_name : [doc_id, loc, url] }, ...
                ## Using the doc id as the index into the array
                tempDocs = [{}]*len(self.doc_key)
                for x in self.doc_key:
                        tempDocs[self.doc_key[x][0]] = { x : self.doc_key[x] }
                self.doc_key = tempDocs

                ## Initialize docVector Array (for storing VSM)
                self.docVector = [ [0]*len(self.index) for _ 
                        in range(len(self.doc_key)) ]
                #self.docVector = [ [0]*len(self.index[0]) for _ 
                #        in range(len(self.doc_key[0])) ]

                ## Restructure proximity and sort
                self.prox = []
                self.mypk = [key for key in sorted(self.proximity.keys())]
                for x in self.mypk:
                        self.prox.append( { x: self.proximity[x] } )
                #self.prox.sort(key = lambda k: k.keys()[0])

                ## Initialize proxVector Array (for storing proximity)
                self.proxVector = [ []*len(self.index) for _
                        in range(len(self.doc_key)) ]

                ## Initialize the termIndex
                self.termIndex = {}

        ## Create tf-idf weight
        #@timing ## Uncomment to see discrete timing
        def genTFIDF(self):
                ## - First create the df for each term
                ## Loop through index and construct Vector Space Model
                for i in range(len(self.index)):
                        #word = self.index[i].keys()[0]
                        word = self.mylist[i]

                        # count non-zero indices in arrays
                        df = len(list(filter(None,self.index[i][word])))

                        # Calculate idf: log(n/df), where n is length 
                        # of array (# of docs)
                        idf = log10(len(self.index[i][word]) / float(df))
                        self.termIndex[word] = [float("{0:.3f}".format(idf))]

                        # Calculate tf-idf weights (not normalized)
                        # |Wi| = sqrt(sum(squared(idf)))
                        weights = self.index[i][word]
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
                        #self.index[i]['df'] = df
                        #self.index[i]['idf'] = "{0:.3f}".format(idf)
                        #self.index[i]['w'] = w

        ## Normalize the vectors using docLength - establish unit vectors
        #@timing ## Uncomment to see discrete timing
        def normalizeVectors(self):
                ## Now finish length of Di (docLength)
                self.docLength = [float("{0:.3f}".format(sqrt(x))) 
                        for x in self.docLength]

                ## Normalize the Document Vector Space Model
                for x in range(len(self.docVector)):
                        for y in range(len(self.docVector[x])):
                                if self.docLength[x] == 0:
                                        self.docVector[x][y] = 0
                                else:
                                        self.docVector[x][y] /= self.docLength[x]
                                
                                self.docVector[x][y] = float("{0:.3f}".format(
                                        self.docVector[x][y]))

        ## Create the proximity and term index
        def genProx(self):
                ## Go through each document
                for d in range(len(self.doc_key)):
                        #doc = self.doc_key[d].keys()[0]
                        ## Go through each term
                        for t in range(len(self.prox)):
                                #term = self.prox[t].keys()[0]
                                term = self.mypk[t]

                                ## Initialize term array
                                self.proxVector[d].append([])

                                ## Build term index if first pass
                                if d < 1:
                                        self.termIndex[term].append(t)

                                ## Go through each tuple
                                for mytuple in self.prox[t][term]:
                                        ## if tuple[0] = d, then append prox
                                        ## for this word
                                        #if mytuple[0] == doc:
                                        if mytuple[0] == d:
                                                self.proxVector[d][t].append(mytuple[1])

        #@timing ## Uncomment to see discrete timing
        def writeOutput(self, outFile):
                ## Write the Document Vector Space Model (docVector) and
                ## the Document Keystone (doc_key) out to the output file
                out = shelve.open(outFile)
                out['docVector'] = self.docVector
                out['doc_key'] = self.doc_key
                out['proxVector'] = self.proxVector
                out['termIndex'] = self.termIndex
                out.close()

##-----------------------------------------------------------------##
## Our 'MAIN' method - fun fun... ;)
##-----------------------------------------------------------------##
@timing
def main():
        ## Execution as an object - result is VSM array
        simpleVSM = genVSMArray(inFile)
        simpleVSM.genTFIDF()
        simpleVSM.normalizeVectors()
        simpleVSM.genProx()
        simpleVSM.writeOutput(outFile)

##-----------------------------------------------------------------##
## Execute the main... pretending to be C :)
##-----------------------------------------------------------------##
if __name__ == "__main__":
        main()
