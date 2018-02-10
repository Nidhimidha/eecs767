import shelve

proc = shelve.open('OUTPUT/processingOutput.db')
docVector = proc['docVector']
doc_key = proc['doc_key']
proc.close()

print docVector
print doc_key
