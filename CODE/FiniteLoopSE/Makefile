.PHONY: help prepenv crawl ingest process query webprep seedata test 

PIP=pip2.7
PYTHON=python
LOC=$(shell pwd)
WEBDIR=~/public_html
CGIDIR=cgi-bin

## Run the webcrawler for 5 minutes 
## (s for seconds, m for minutes, h for hours)
DURATION=1m

## The base path variable in ingest.py
#INGPATH=$(LOC)/INPUT/cached_docs/
INGPATH=$(LOC)/INPUT/control/
OUTPATH=$(LOC)/OUTPUT/

## Directory structure
##	Makefile
##	cgi-bin
##		search.cgi
##	index.html
##      INPUT
##	        cached_docs
##                      *.htm(l)
##              control
##                      *.txt
##              docsnew
##                      *.htm(l)
##              docsnew.zip
##	OUTPUT
##              ingestOutput.db
##              processingOutput.db
##	src
##		ingest.py
##		processing.py
##		query.py
##		seeShelve.py
##		web_crawler.py

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
	@echo "make query"
	@echo "         run the query module - for testing purposes"
	@echo "make webprep"
	@echo "		transfer files to web directory and update permissions"
	@echo "		(permissions set for chroot webserver environment)"
	@echo "make seedata"
	@echo "		display the contents of the processed data"
	@echo "make test"
	@echo "		perform ingest and processing of corpus with detailed timing"
	@echo "		outputs 00ingest.timing and 00processing.timing files"

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
		
## Keep in mind - the crawler will run for the DURATION specified above...
crawl: src/web_crawler.py $(INGPATH)
	## It will claim failure... but only because I've killed it with the
	## timeout
	timeout $(DURATION) $(PYTHON) src/web_crawler.py

## DEV NOTES
## ---------------------------------------------
## Added to ingest.py after setting of path variable (to accept command line)
## (Around line 55)
## if ( len(sys.argv) > 1 ):
##		path = sys.argv[1]
## Commented out json data production
## (Around line 330)
## # index_data.func_json_out()#May be useful for debugging

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

## Test query
query: src/query.py src/ingest.py $(OUTPATH)processingOutput.db
	$(PYTHON) src/query.py $(OUTPATH)processingOutput.db \
                $(OUTPATH)ingesOutput.db

## Prepare for web
webprep: src/query.py $(OUTPATH)processingOutput.db index.html $(CGIDIR)/search.cgi
	## Copy the data into the public_html area
	cp index.html $(WEBDIR)
	if [ ! -d $(WEBDIR)/$(CGIDIR) ];then \
		mkdir $(WEBDIR)/$(CGIDIR) \
		chmod 755 $(WEBDIR)/$(CGIDIR) \
	fi
	cp $(CGIDIR)/search.cgi $(WEBDIR)/$(CGIDIR)
	cp $(OUTPATH)processingOutput.db $(WEBDIR)/$(CGIDIR)
	chmod 744 $(WEBDIR)/$(CGIDIR)/search.cgi
		
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
clean: $(INGPATH) $(WEBDIR) $(WEBDIR)/$(CGIDIR)
	rm -f $(OUTPATH)*
	rm -f $(INGPATH)*
	if [ -f $(WEBDIR)/index.html ];then \
		rm -f $(WEBDIR)/index.html \
	fi
	if [ -f $(WEBDIR)/$(CGIDIR)/search.cgi ];then \
		rm -f $(WEBDIR)/$(CGIDIR)/search.cgi \
	fi
	if [ -f $(WEBDIR)/$(CGIDIR)/query.py ];then \
		rm -f $(WEBDIR)/$(CGIDIR)/query.py \
	fi
	if [ -f $(WEBDIR)/$(CGIDIR)/ingest.py ];then \
		rm -f $(WEBDIR)/$(CGIDIR)/ingest.py
	fi
