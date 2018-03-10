import shelve                   ## For generating datastructure db files
from math import log10, sqrt    ## Doing a little math...
import time                     ## For Timing
from functools import wraps     ## For Timing

inFile = 'OUTPUT/ingestOutput'
outFile = 'OUTPUT/processingOutput'

##-------------------------------------------------------------------------##
## INPUT
## Processing Component of Search Engine Space (follows ingest - preceeds
## Query execution
##-------------------------------------------------------------------------##
## index = [
##       { Term1: [tf1, tf2, ..., tfn] },
##       { Term2: [tf1, tf2, ..., tfn] },
##       ...,
##       { Termm: [tf1, tf2, ..., tfn] }
## ]
## doc_key = [
##       { DocName1: [DocID1, DocLocation1] },
##       { DocName2: [DocID2, DocLocation2] },
##       ...,
##       { DocNamen: [DocIDn, DocLocationn] }
## ]
## proximity = {
##       Term1: [ [DocID, Prox], [DocID, Prox], ..., [DocID, Prox] ],
##       Term2: [ [DocID, Prox], [DocID, Prox], ..., [DocID, Prox] ],
##       ...,
##       Termm: [ [DocID, Prox], [DocID, Prox], ..., [DocID, Prox] ]
## }
##-------------------------------------------------------------------------##
## OUTPUT
##-------------------------------------------------------------------------##
## doc_key = [
##      { DocName1: [DocID1, DocLocation1] },
##      { DocName2: [DocID2, DocLocation2] },
##      ...,
##      { DocNamen: [DocIDn, DocLocationn] }
## ]
## docVector = [
##      [WT1,D1, WT1,D2, ..., WT1,Dn],
##      [WT2,D1, WT2,D2, ..., WT2,Dn],
##      ...,
##      [WTm,D1, WTm,D2, ..., WTm,Dn]
## ]
## proxVector = [
##      [ [P1T1,D1, P2T1,D1, ..., PiT1D1], 
##        [P1T1,D2, P2T1,D2, ..., PiT1D2],
##        ..., 
##        [P1T1,Dn, P2T1,Dn, ..., PiT1Dn] ],
##      [ [P1T2,D1, P2T2,D1, ..., PiT2D1], 
##        [P1T2,D2, P2T2,D2, ..., PiT2D2], 
##        ..., 
##        [P1T2,Dn, P2T2,Dn, ..., PiT2Dn] ],
##      ...,
##      [ [P1Tm,D1, P2Tm,D1, ..., PiTmD1], 
##        [P1Tm,D2, P2Tm,D2, ..., PiTmD2], 
##        ..., 
##        [P1Tm,Dn, P2Tm,Dn, ..., PiTmDn] ]
## ] 
## termIndex = {
##      Term1: i1,
##      Term2: i2,
##      ...,
##      Termm: im
## }
##-------------------------------------------------------------------------##

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
                self.proximity = ingest['proximity']
                ingest.close()

                ## Sort the index and proximity (need to match)
                self.index.sort(key=lambda k: k.keys()[0])

                ## Initialize docLength Array (for normalizing weights)
                w = self.index[0].keys()[0]
                self.docLength = [0]*len(self.index[0][w])
                
                ## Initialize docVector Array (for storing VSM)
                self.docVector = [ [0]*len(self.index) for _ 
                        in range(len(self.doc_key)) ]

                ## Restructure proximity and sort
                self.prox = []
                for x in self.proximity:
                        self.prox.append( { x: self.proximity[x] } )
                self.prox.sort(key = lambda k: k.keys()[0])

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

        ## Create the proximity and term index
        def genProx(self):
                ## Go through each document
                for d in range(len(self.doc_key)):
                        doc = self.doc_key[d].keys()[0]
                        ## Go through each term
                        for t in range(len(self.prox)):
                                term = self.prox[t].keys()[0]
                                ## Initialize term array
                                self.proxVector[d].append([])

                                ## Build term index if first pass
                                if d < 1:
                                        self.termIndex[term] = t

                                ## Go through each tuple
                                for tuple in self.prox[t][term]:
                                        ## if tuple[0] = d, then append prox
                                        ## for this word
                                        if tuple[0] == doc:
                                                self.proxVector[d][t].append(tuple[1])

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
