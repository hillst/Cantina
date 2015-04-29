#!/usr/bin/env python
from invoke import task, run

@task(help={"files":"Runs the full pipeline on the passed fastq files. It's important to note that in order to use wildcard dilemeters you MUST surround them with quotes."})
def all(files="*.fastq"):
    run("echo 'hello from build'")
    blast(files)

@task
def clean(all=False):
    if all:
        run("rm -rf blastdb")
        run("rm -rf wgs_reads")
    run("rm -rf velvet*")
    run("rm -rf extracted_reads/*.fastq") 

@task
def setup():
    run("echo 'setting up directory'")
    run("mkdir wgs_reads")
    run("mkdir blastdb")
    run("mkdir extracted_reads")  
"""
Reals tasks
"""
@task
def sort_fastq(files):
    print files
    run("mkdir tmp")
    run("export TMPDIR=tmp")
    run("echo 'sort files'")
    run("rm -rf tmp")
    

@task
def blast_db(files="wgs_reads/database.fastq", blastdb_dir="blastdb"):
    title="some_parse_command"
    run("makeblastdb -type nucl -in " + files + " -title " + title)

@task
def blast(files="*.fastq"):
    run("echo 'hello from blast'")
    run("ls " + files)

"""
task for building databases
task for sorting files
task for extracting reads
task for assembling reads

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
#i don't understand this part but maybe i should? exonerate i thought we used for "ORDER" and then scaffolding or some shit
echo "determining order of contigs"
#blastn -db Blast/hlcat -query Bitter/contigs.fa

echo "ordering contigs"

echo "closing contig gaps with Ns"

echo "running exonerate"



TODO:
-Quantify how much we improved the assembly by
-Handle a process failing (probably by running via java or python)
-Figure out when to stop iterating.
-Add new reads to the previous set

ALSO NOTE:
    what we are doing is basically overlap graph but with a crazy process that does local assembly to improve the assembly
"""
