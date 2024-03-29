import shelve                   ## For generating datastructure db files
from math import log10, sqrt    ## Doing a little math...
import time                     ## For Timing
from functools import wraps     ## For Timing

inFile = 'OUTPUT/ingestOutput.db'
outFile = 'OUTPUT/processingOutput'
artFile = 'OUTPUT/processingArtifacts'

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
                print("    Initializing Processing")

                ## Pull in the data structure(s) from ingest
                print("        Ingesting ", inFile)
                try:
                        ingest = shelve.open(inFile)
                except:
                        x = inFile.replace('.db','')
                        ingest = shelve.open(x)
                        pass

                ## Data from ingest
                self.index = ingest['index']
                self.doc_key = ingest['doc_key']
                self.proximity = ingest['proximity']
                self.numdocs = ingest['num_docs']
                self.titles = ingest['title_map']
                ingest.close()

                ## Sort the index and proximity (need to match)
                ## Need to modify from
                ## { term : [counts], ...
                ## to
                ## [ {term : [counts] }, ...
                ## In order to sort
                print("        Sorting Index")
                self.mylist = [key for key in sorted(self.index.keys())]
                tempIndex = []
                for x in self.mylist:
                        tempIndex.append( { x : self.index[x] } )
                self.index = tempIndex

                ## Initialize docLength Array (for normalizing weights)
                w = self.mylist[0]
                self.docLength = [0]*len(self.index[0][w])
                
                ## Need to modify the doc_key from
                ## { doc_name : [doc_id, loc, url], ...
                ## to
                ## [ { doc_name : [doc_id, loc, url] }, ...
                ## Using the doc id as the index into the array
                ## Length of array based on numdocs from ingest
                print("        Sorting doc_key")
                tempDocs = [{}]*self.numdocs
                for x in self.doc_key:
                        tempDocs[self.doc_key[x][0]] = { x : self.doc_key[x] }
                self.doc_key = tempDocs

                ## Initialize docVector Array (for storing VSM)
                ## Length of array based on numdocs from ingest
                self.docVector = [ [0]*len(self.index) for _ 
                        in range(self.numdocs) ]

                ## Restructure proximity and sort
                print("        Sorting proximity")
                self.prox = []
                self.mypk = [key for key in sorted(self.proximity.keys())]
                for x in self.mypk:
                        self.prox.append( { x: self.proximity[x] } )

                ## Initialize proxVector Array (for storing proximity)
                self.proxVector = {}
                #self.proxVector = [ []*len(self.index) for _
                #        in range(len(self.doc_key)) ]

                ## Initialize the termIndex, termDict
                self.termIndex = {}
                for i in range(len(self.mypk)):
                        self.termIndex[self.mypk[i]] = [i]

                self.termDict = {}

        ## Create tf-idf weight
        #@timing ## Uncomment to see discrete timing
        def genTFIDF(self):
                print("    Generating Vector Space Model")

                ## - First create the df for each term
                ## Loop through index and construct Vector Space Model
                print("        Looping through the index")
                for i in range(len(self.index)):
                        word = self.mylist[i]

                        # count non-zero indices in arrays
                        df = len(list(filter(None,self.index[i][word])))

                        # Calculate idf: log(n/df), where n is length 
                        # of array (# of docs)
                        idf = log10(len(self.index[i][word]) / float(df))
                        
                        # Store the term IDF
                        #self.termIndex[word] = [float("{0:.3f}".format(idf))]
                        self.termIndex[word].insert(0,
                                float("{0:.3f}".format(idf)))

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

        ## Normalize the vectors using docLength - establish unit vectors
        #@timing ## Uncomment to see discrete timing
        def normalizeVectors(self):
                print("    Normalizing Vectors")
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
        ## Create a term dictionary - must be after genProx (for termIndex) 
        def genTermDict(self):
                print("    Creating term vector dictionary")

                ## Go through the termIndex and create the dictionary
                print("        Building Dictionary")
                for k in self.termIndex:
                        wi = self.termIndex[k][1]
                        termWeights = []
                        for i in range(len(self.docVector)):
                                if self.docVector[i][wi] > 0:
                                        termWeights.append([i, self.docVector[i][wi]])

                        ## Save the array
                        self.termDict[k] = termWeights


        ## Create the proximity
        def genProx(self):
                print("    Modifying proximity")

                for t in range(len(self.prox)):
                        term = self.mypk[t]
                        
                        ## Initialize document dictionary for term
                        self.proxVector[term] = {}

                        ## Go through each tuple
                        for mytuple in self.prox[t][term]:
                                ## First value is the doc (key)
                                ## Second value is a prox
                                if mytuple[0] not in self.proxVector[term]:
                                        ## Initialize key
                                        self.proxVector[term][mytuple[0]] = []

                                self.proxVector[term][mytuple[0]].append(mytuple[1])

                ## Go through each document
#                for d in range(self.numdocs):
#                        ## Go through each term
#                        for t in range(len(self.prox)):
#                                term = self.mypk[t]
#
#                                ## Initialize term array
#                                self.proxVector[d].append([])
#
#                                ## Build term index if first pass
#                                if d < 1:
#                                        print(term,"::",t)
#                                        self.termIndex[term].append(t)
#
#                                ## Go through each tuple
#                                for mytuple in self.prox[t][term]:
#                                        if mytuple[0] == d:
#                                                self.proxVector[d][t].append(mytuple[1])

        #@timing ## Uncomment to see discrete timing
        def writeOutput(self, outFile):
                print("    Writing output file: ", outFile)
                ## Write the Document Vector Space Model (docVector) and
                ## the Document Keystone (doc_key) out to the output file
                out = shelve.open(outFile)
                out['doc_key'] = self.doc_key
                out['termDict'] = self.termDict
                out['proxDict'] = self.proxVector
                out['termIDF'] = self.termIndex
                out['title_map'] = self.titles
                out.close()
                
                print("    Writing out artifacts: ", artFile)
                art = shelve.open(artFile)
                art['docVector'] = self.docVector
                art.close()


##-----------------------------------------------------------------##
## Our 'MAIN' method - fun fun... ;)
##-----------------------------------------------------------------##
@timing
def main():
        print("Processing")
        ## Execution as an object - result is VSM array
        simpleVSM = genVSMArray(inFile)
        simpleVSM.genTFIDF()
        simpleVSM.normalizeVectors()
        simpleVSM.genProx()
        simpleVSM.genTermDict()
        simpleVSM.writeOutput(outFile)

##-----------------------------------------------------------------##
## Execute the main... pretending to be C :)
##-----------------------------------------------------------------##
if __name__ == "__main__":
        main()
