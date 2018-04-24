#!/bin/bash

base="python3 src/html_summary.py"
cache="INPUT/cached_docs"
procDB='OUTPUT/processingOutput.db'
filecount=`ls -l INPUT/cached_docs | wc -l`
countpp=10
parts=$((filecount / countpp + 1))
numproc=`nproc --all`

# Don't want to run more processes than the system can handle
# Only use 1/2 the processors
procs=$((numproc / 2))
ppp=$((parts / procs + 1))

i=1
processes=()
part=1
# For each core
while [ $i -le $procs ];
do
	cmdstr="screen -dm bash -c '"

	# For each process (part + (ppp * countpp)
	#group=$((part + ppp * countpp - 1))
	group=$((part + ppp))
	# For each process queue group
	while [ $part -le $group -a $part -le $(($parts + 1)) ];
	do
		cmdstr+="$base $cache $procDB $part;"
		#((part=`expr $part + $countpp`))
		((part++))
	done
	cmdstr+="'"

	## Execute this proc
	if [ "$cmdstr" != "screen -dm bash -c ''" ];
	then
		echo $cmdstr
		eval $cmdstr
	fi

	# Next proc
	((i++))
done


#python3 src/html_summary.py INPUT/cached_docs  OUTPUT/processingOutput.db 17
