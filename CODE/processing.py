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
##      { term: [tfs array] },
##      { '/A-Za-z0-9/*': [ /0-9/*, ..., /0-9/* ] },
##      ...,
##      { '/A-Za-z0-9/*': [ /0-9/*, ..., /0-9/* ] }
##  doc_key = [
##      { docName: [id, path] },
##      { '/A-Za-z0-9/*': [/A-Za-z0-9/*, /A-Za-z0-9/* },
##      ...,
##      { '/A-Za-z0-9/*': [/A-Za-z0-9/*, /A-Za-z0-9/* }
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
                self.index.sort(key=lambda k: k.keys()[0])

                ## Initialize docLength Array (for normalizing weights)
                w = self.index[0].keys()[0]
                self.docLength = [0]*len(self.index[0][w])
                
                ## Initialize docVector Array (for storing VSM)
                self.docVector = [ [0]*len(self.index) for _ in range(len(self.doc_key)) ]
            
        ## Create tf-idf weight
        #@timing ## Uncomment to see discrete timing
        def genTFIDF(self):
                ## - First create the df for each term
                ## Loop through index and construct Vector Space Model
                for i in range(len(self.index)):
                        word = self.index[i].keys()[0]
                        # count non-zero indices in arrays
                        df = len(list(filter(None,self.index[i][word])))

                        # Calculate idf: log(n/df), where n is length 
                        # of array (# of docs)
                        idf = log10(len(self.index[i][word]) / float(df))

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
## Our 'MAIN' method - fun fun... ;)
##-----------------------------------------------------------------##
@timing
def main():
        ## Execution as an object - result is VSM array
        simpleVSM = genVSMArray('OUTPUT/ingestOutput')
        simpleVSM.genTFIDF()
        simpleVSM.normalizeVectors()
        simpleVSM.writeOutput('OUTPUT/processingOutput')

##-----------------------------------------------------------------##
## Execute the main... pretending to be C :)
##-----------------------------------------------------------------##
if __name__ == "__main__":
        main()
