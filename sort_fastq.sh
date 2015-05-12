#!/bin/bash
export TMPDIR=tmpdir
FASTQ=$1
BASENAME=`basename $FASTQ .fastq`
cat $FASTQ | paste - - - - | sort -k1,1 -t " " | tr "\t" "\n" > $BASENAME.sorted.fastq
