#!/bin/bash


echo "targeting unaligned raw reads"
#blastn -db blastdb/250bp_assembled -query notFound.fasta -outfmt 6 -num_threads 8 > 250bp.blastn
#blastn -db blastdb/143bp_assembled -query notFound.fasta -outfmt 6 -num_threads 8 > 143bp.blastn
#blastn -db blastdb/173bp_assembled -query notFound.fasta -outfmt 6 -num_threads 8 > 173bp.blastn
echo "splitting results by contig..."

echo "finding reads..."
python ~/bin/getBlastRawReads.py -b 250bp.blastn  -r raw_reads/250bp_teamaker.assembled.sorted.fastq
python ~/bin/getBlastRawReads.py -b 143bp.blastn  -r raw_reads/143bp_teamaker.assembled.sorted.fastq
python ~/bin/getBlastRawReads.py -b 173bp.blastn  -r raw_reads/173bp_teamaker.assembled.sorted.fastq
echo "performing assembly..."
for file in *.fastq;
do
    BASENAME=`basename $file .fastq`
    velveth $BASENAME 51 -short -fastq $file 
    velvetg $BASENAME -exp_cov auto 
    #need an exonerate step :(
    #exonerate --model est2genome --query ../hlcat2.fasta --target mergedScaffolds.fasta
done;

echo "determining order of contigs"
blastn -db Blast/hlcat -query Bitter4/contigs.fa -outfmt 6 > 2504Blast.txt
echo "ordering contigs"
python orderContigs.py Bitter4/contigs.fa 2504Blast.txt > mergedScaffolds4.fasta
echo "running exonerate"
exonerate --model est2genome --query ../hlcat2.fasta --target mergedScaffolds4.fasta

#i don't understand this part but maybe i should? exonerate i thought we used for "ORDER" and then scaffolding or some shit
echo "determining order of contigs"
#blastn -db Blast/hlcat -query Bitter/contigs.fa

echo "ordering contigs"

echo "closing contig gaps with Ns"

echo "running exonerate"


"""

TODO:
-Quantify how much we improved the assembly by
-Handle a process failing (probably by running via java or python)
-Figure out when to stop iterating.
-Add new reads to the previous set

ALSO NOTE:
    what we are doing is basically overlap graph but with a crazy process that does local assembly to improve the assembly
"""
