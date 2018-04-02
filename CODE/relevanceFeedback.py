import query
from query import *
import shelve

## INPUT
##-------------------------------------------------------------------------##
## relevantDocs = [
##      [ DocName1, DocLocation1],
##      [ DocName2, DocLocation2],
##      …,
##      [ DocNamen, DocLocationn]
## ]
## irrelevantDocs = [
##      [ DocName1, DocLocation1],
##      [ DocName2, DocLocation2],
##      …,
##      [ DocNamen, DocLocationn]
##  ]
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

## OUTPUT
##-------------------------------------------------------------------------##
## results = [
##      [ DocName1, DocLocation1, Rank1, Summary1],
##      [ DocName2, DocLocation2, Rank2, Summary2],
##      …,
##      [ DocNamen, DocLocationn, Rankn, Summaryn]
##  ]

class relevance:
    def __init__(self, infile, infile1):
        proc = shelve.open(infile)
        self.docVector = proc['docVector']
        proc.close()
        query = shelve.open(infile1)
        self.queryVector = query['queryVector']
        query.close()

    ## On click of Refine Search Button
    def relevanceFeedback(self,relevantDocs, irrelevantDocs):
        a = 0.5
        b = 0.5
        c = -0.1

        releNum = float(len(relevantDocs))
        irreleNum = float(len(irrelevantDocs))

        docVectorIndices = []
        for i in range(len(relevantDocs)):
            docVectorIndices.append(int(relevantDocs[i][1:]) - 1)
        relevantDocVectors = [self.docVector[i] for i in docVectorIndices]
        totalReleVec = [sum(i) for i in zip(*relevantDocVectors)]

        docVectorIndices = []
        for i in range(len(irrelevantDocs)):
            docVectorIndices.append(int(irrelevantDocs[i][1:]) - 1)
        irrelevantDocVectors = [self.docVector[i] for i in docVectorIndices]
        totalIrreleVec = [sum(i) for i in zip(*irrelevantDocVectors)]

        if releNum == 0:
            if irreleNum != 0:
                c = c/irreleNum
                newIrreleVec = [k * c for k in totalIrreleVec]
                updatedQuery = [i * a for i in self.queryVector]

                newQ = [sum(x) for x in zip(updatedQuery,newIrreleVec)]
                return newQ
            else:
                newQ = self.queryVector
                return newQ

        if irreleNum == 0:
            b =b/releNum
            newReleVec = [j * b for j in totalReleVec]
            updatedQuery = [i * a for i in self.queryVector]

            newQ = [sum(x) for x in zip(updatedQuery, newReleVec)]
            return newQ

        else:
            b=b/releNum
            c=c/irreleNum
            newReleVec = [j * b for j in totalReleVec]
            newIrreleVec = [k * c for k in totalIrreleVec]
            updatedQuery = [i * a for i in self.queryVector]

            newQ = [sum(x) for x in zip(updatedQuery, newReleVec,newIrreleVec)]
            return newQ

    def calcSimilarity(self,normalizedQuery):
        similarity(normalizedQuery)
        showResult()



def main():
            relInstance = relevance('OUTPUT/processingOutput', 'OUTPUT/queryOutput')
            ## TODO: get the relevant and irrelevant docs list from cgi
            newQuery = relInstance.relevanceFeedback(['D2','D3'],['D4'])
            relInstance.calcSimilarity(newQuery)


if __name__ == "__main__":
            main()


