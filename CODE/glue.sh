#!/bin/bash


diag=false

usage="$(basename "$0") [-h] [-d] -- program to run the search engine

where:
	-h show this help text
	-d run with diagnostic output"

case "$1" in
	-h) echo "$usage"
		exit
		;;
	-d) echo "Running Diagnostics"
		diag=true
		;;
	"")	;;
	*) printf "unknown option: -%s\n" "$OPTARG" >&2
		echo "$usage" >&2
		exit 1
		;;
esac

if [ $diag = true ];
then
	python -m cProfile ingestTEMPLATE.py > 00ingest.diag
	python -m cProfile processing.py > 00process.diag
	python -m cProfile query.py > 00query.diag
	echo "Diagnostic Results written to *.diag files"
else
	python ingestTEMPLATE.py
	python processing.py
	python query.py
fi

exit
