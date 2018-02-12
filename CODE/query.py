import shelve

proc = shelve.open('OUTPUT/processingOutput')
docVector = proc['docVector']
doc_key = proc['doc_key']
proc.close()

print(docVector)
print(doc_key)
