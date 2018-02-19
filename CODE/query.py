import shelve
from processing import TermNode, DocLL

proc = shelve.open('OUTPUT/processingOutput')

# For array output
docVector = proc['docVector']
doc_key = proc['doc_key']
proc.close()

#print(docVector)
#print(doc_key)

# For linked list output

