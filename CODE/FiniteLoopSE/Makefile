.PHONY: help go prepenv crawl ingest process query webprep seedata test clean

PIP=pip3
#PIP=pip2.7
#PYTHON=python
PYTHON=python3
LOC=$(shell pwd)
WEBDIR=~/public_html
CGIDIR=cgi-bin

## Run the webcrawler for 5 minutes 
## (s for seconds, m for minutes, h for hours)
DURATION=1m

## The base path variable in ingest.py
## Deployed System
INGPATH=$(LOC)/INPUT/cached_docs/
## Provided dataset - be sure to unzip INPUT/docsnew.zip
#INGPATH=$(LOC)/INPUT/docsnew/
## Control dataset based on class quiz (control group)
#INGPATH=$(LOC)/INPUT/control/
OUTPATH=$(LOC)/OUTPUT/

.DEFAULT: help
help:
	@echo "make prepenv"
	@echo "		locally installs nltk and downloads stopwords list"
	@echo "make go"
	@echo "		runs ingest, process, and webprep"
	@echo "make crawl"
	@echo "		perform niche crawler (runs for $(DURATION))"
	@echo "make ingest"
	@echo "		perform ingest of corpus"
	@echo "make process"
	@echo "		perform processing of corpus"
	@echo "make query"
	@echo "		run the query module - for testing purposes"
	@echo "make webprep"
	@echo "		transfer files to web directory and update permissions"
	@echo "		(permissions set for chroot webserver environment)"
	@echo "make seedata"
	@echo "		display the contents of the processed data"
	@echo "make test"
	@echo "		perform ingest and processing of corpus with detailed timing"
	@echo "		outputs 00ingest.timing and 00processing.timing files"
	@echo "make clean"
	@echo "		removes:"
	@echo "			$(WEBDIR)/search.html"
	@echo "			$(WEBDIR)/$(CGIDIR)/search.cgi"
	@echo "			$(WEBDIR)/$(CGIDIR)/query.py"
	@echo "			$(WEBDIR)/$(CGIDIR)/ingest.py"
	@echo "			$(WEBDIR)/$(CGIDIR)/processingOutput.db"
	@echo "			$(WEBDIR)/$(CGIDIR)/__pycache__"
	@echo "			src/ingest.pyc"
	@echo "			src/__pycache__"

## To simply... make it go (excludes webcrawl)
go: ingest process webprep

## Prepare the environment
## Make sure that nltk is installed - assume no sudo permissions, just place
## locally for the individual...
prepenv:		
	## Make sure that nltk is installed
	$(PIP) install --user nltk
	## Import the stopwords
	$(PYTHON) -c "import nltk; \
		from nltk.stem.porter import *; \
		from nltk.corpus import stopwords; \
		from collections import defaultdict;"
	mkdir INPUT/cached_docs
	mkdir OUTPUT
		
## Keep in mind - the crawler will run for the DURATION specified above...
crawl: src/web_crawler.py $(INGPATH)
	## It will claim failure... but only because I've killed it with the
	## timeout
	timeout $(DURATION) $(PYTHON) src/web_crawler.py $(INGPATH)

## Ingest the data - prepare for the processing module
ingest: src/ingest.py $(INGPATH) $(OUTPATH)
	## Need to make sure that OUTPUT has download_manifest.db
	## Depending on python version (minor), may have been created
	## without .db extension
	if [ -f $(INGPATH)download_manifest ];then \
		mv $(INGPATH)download_manifest $(INGPATH)download_manifest.db; \
	fi

	$(PYTHON) src/ingest.py "$(INGPATH)"

	## Need to make sure that OUTPUT has ingestOutput.db
	## Depending on python version (minor), may have been created
	## without .db extension
	if [ -f $(OUTPATH)ingestOutput ];then \
		mv $(OUTPATH)ingestOutput $(OUTPATH)ingestOutput.db; \
	fi

## Process the data - prepare for the query module
process: src/processing.py $(OUTPATH)ingestOutput.db
	$(PYTHON) src/processing.py

	## Make sure processingOutput has .db too
	if [ -f $(OUTPATH)processingOutput ]; then \
		mv $(OUTPATH)processingOutput $(OUTPATH)processingOutput.db; \
	fi
	
	## Copy processingOutput.db to the local cgi-bin directory
	cp $(OUTPATH)processingOutput.db $(CGIDIR)/

## Test query
query: src/query.py src/ingest.py $(OUTPATH)processingOutput.db
	$(PYTHON) src/query.py 

## Prepare for web
webprep: src/ingest.py src/query.py $(OUTPATH)processingOutput.db search.html $(CGIDIR)/search.cgi
	## Copy the latest source to the local cgi-bin
	cp src/query.py src/ingest.py $(CGIDIR)

	## Copy the data into the public_html area
	cp search.html $(WEBDIR)
	cp -R $(CGIDIR)/* $(WEBDIR)/$(CGIDIR)
	chmod 744 $(WEBDIR)/$(CGIDIR)/search.cgi
	chmod 744 $(WEBDIR)/$(CGIDIR)/*.py
	chmod 744 $(WEBDIR)/$(CGIDIR)/*.db
		
## Use seeShelve.py to see the contents of the shelve
## database files
seedata: $(OUTPATH) src/seeShelve.py
	$(PYTHON) src/seeShelve.py

## Detailed timing runs
test: src/ingest.py src/processing.py $(OUTPATH) src/cached_docs
	$(PYTHON) -m cProfile src/ingest.py > 00ingest.timing
	$(PYTHON) -m cProfile src/processing.py > 00 processing.py

## Clean up... the only thing we want to leave behind is the
## CGIDIR... mainly because we don't know if we created it or
## if it was already there....
clean: $(WEBDIR) $(WEBDIR)/$(CGIDIR)
	## Systematically clean up after ourselves
	## Clean the web area
	rm -f $(WEBDIR)/search.html 
	rm -f $(WEBDIR)/$(CGIDIR)/search.cgi 
	rm -f $(WEBDIR)/$(CGIDIR)/query.py 
	rm -f $(WEBDIR)/$(CGIDIR)/ingest.py 
	rm -f $(WEBDIR)/$(CGIDIR)/processingOutput.db 
	rm -rf $(WEBDIR)/$(CGIDIR)/__pycache__ 
	## Clean our own house
	rm -f $(CGIDIR)/query.py 
	rm -f $(CGIDIR)/ingest.py 
	rm -f $(CGIDIR)/ingest.pyc 
	rm -f $(CGIDIR)/processingOutput.db 
	rm -rf $(CGIDIR)/__pycache__ 
	rm -f src/ingest.pyc 
	rm -rf src/__pycache__ 
