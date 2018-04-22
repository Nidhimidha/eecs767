.PHONY: help prepenv crawl ingest process html webprep seedata clean

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
OUTCACHE=$(OUTPATH)CACHE/

.DEFAULT: help
help:
	@echo "make prepenv"
	@echo "		locally installs nltk and downloads stopwords list"
	@echo "make crawl"
	@echo "		perform niche crawler (runs for $(DURATION))"
	@echo "make ingest"
	@echo "		perform ingest of corpus"
	@echo "make process"
	@echo "		perform processing of corpus"
	@echo "make html"
	@echo "		create html text summaries (saved at $(OUTCACHE)"
	@echo "make query"
	@echo "		run the query module - for testing purposes"
	@echo "make webprep"
	@echo "		transfer files to web directory and update permissions"
	@echo "		(permissions set for chroot webserver environment)"
	@echo "make seedata"
	@echo "		display the contents of the processed data"
	@echo "make clean"
	@echo "		removes copied falls from:"
	@echo "			$(WEBDIR)"
	@echo "			$(WEBDIR)/$(CGIDIR)"
	@echo "			$(OUTCACHE)
	@echo "			src/ingest.pyc"
	@echo "			src/__pycache__"

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
	mkdir OUTPUT/CACHE
		
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
	
	## Make sure processingArtifacts has .db too
	if [ -f $(OUTPATH)processingArtifacts ]; then \
		mv $(OUTPATH)processingArtifacts $(OUTPATH)processingArtifacts.db; \
	fi
	
	## Copy processingOutput.db to the local cgi-bin directory
	cp $(OUTPATH)processingOutput.db $(CGIDIR)/

## Prepare html summaries
html: src/html_summary.py $(OUTPATH)processingOutput.db $(INGPATH)
	$(PYTHON) src/html_summary.py $(INGPATH) $(OUTPATH)processingOutput.db

	## Copy processingOutput.db to the local cgi-bin directory
	cp -R $(OUTCACHE) $(CGIDIR)/

## Test query
query: src/query.py src/ingest.py $(OUTPATH)processingOutput.db
	$(PYTHON) src/query.py 

## Prepare for web
webprep: src/ingest.py src/query.py $(OUTPATH)processingOutput.db search.html $(CGIDIR)/search.cgi
	## Copy the latest source to the local cgi-bin
	cp src/query.py src/ingest.py $(CGIDIR)
	cp -R $(OUTCACHE) $(CGIDIR)

	## Copy the data into the public_html area
	cp search.html $(WEBDIR)
	cp -R $(CGIDIR)/* $(WEBDIR)/$(CGIDIR)
	chmod 744 $(WEBDIR)/$(CGIDIR)/search.cgi
	chmod 744 $(WEBDIR)/$(CGIDIR)/*.py
	chmod 744 $(WEBDIR)/$(CGIDIR)/*.db
	chmod -R 744 $(WEBDIR)/$(CGIDIR)/CACHE
		
## Use seeShelve.py to see the contents of the shelve
## database files
seedata: $(OUTPATH) src/seeShelve.py
	$(PYTHON) src/seeShelve.py

## Clean up... the only thing we want to leave behind is the
## CGIDIR... mainly because we don't know if we created it or
## if it was already there....
clean: $(OUTPATH) $(WEBDIR) $(WEBDIR)/$(CGIDIR)
	## Systematically clean up after ourselves
	## Clean the OUTPUT folder
	rm -f $(OUTPATH)/processingOutput.db
	rm -f $(OUTPATH)/processingArtifacts.db
	rm -f $(OUTPATH)/htmlData.db
	rm -f $(OUTCACHE)/*.db
	## Clean the web area
	rm -f $(WEBDIR)/search.html 
	rm -f $(WEBDIR)/$(CGIDIR)/search.cgi 
	rm -f $(WEBDIR)/$(CGIDIR)/query.py 
	rm -f $(WEBDIR)/$(CGIDIR)/ingest.py 
	rm -f $(WEBDIR)/$(CGIDIR)/processingOutput.db 
	rm -f $(WEBDIR)/$(CGIDIR)/htmlData.db 
	rm -rf $(WEBDIR)/$(CGIDIR)/__pycache__ 
	rm -rf $(WEBDIR)/$(CGIDIR)/CACHE
	## Clean our own house
	rm -f $(CGIDIR)/query.py 
	rm -f $(CGIDIR)/ingest.py 
	rm -f $(CGIDIR)/ingest.pyc 
	rm -f $(CGIDIR)/processingOutput.db 
	rm -f $(CGIDIR)/htmlData.db
	rm -rf $(CGIDIR)/__pycache__ 
	rm -rf $(OUTCACHE)/*.db
	rm -f src/ingest.pyc 
	rm -rf src/__pycache__ 
