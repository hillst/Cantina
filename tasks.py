#!/home/pi/hillst/.local/bin/inv
from invoke import task, run
import os
"""
We are allowed to make a set of assumptions, much like make, and treat them as global variables

Assumptions 
1) Files in wgs_reads have the same name prefix as the blast databases
2) Sorted files have the same basename and end in .sorted.fastq, they don't have a special directory right now
"""
TARGETS="targets.fa"
BLASTN="blastn"
THREADS="64"
GET_READS="~/bin/getBlastRawReads.py"
K="31"

@task(help={"files":"Runs the full pipeline on the passed fastq files. It's important to note that in order to use wildcard dilemeters you MUST surround them with quotes."})
def all():
    run("echo 'hello from build'")

@task
def pipeline():
    blast_all()
    extract_reads()
    assemble_reads()

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
    run("mkdir blast_results")
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
def blast_db(files="wgs_reads/*.fastq", blastdb_dir="blastdb"):
    title="some_parse_command"
    print "do some stuff with the os call to expand the wildcard and makea blast db for all of these"
    #run("makeblastdb -type nucl -in " + files + " -title " + title)

@task
def blast_all():
    print "running blast"
    databases = set([thing.split(".")[0] for thing in os.listdir("blastdb")])
    for database in databases:
        if database != "targets":
            run(BLASTN + " " + "-num_threads " + THREADS + " -query " + TARGETS + " -db blastdb/" + database + " -outfmt 6 > blast_results/" + database + ".blastn")

@task
def extract_reads():
    print "extracting reads"
    for result in os.listdir("blast_results"):
        basename = result.split(".")[0]
        run("python " + GET_READS + " -b blast_results/"+result + " -r wgs_reads/" + basename +".sorted.fastq" + " -t " + THREADS)
    run("mv *.fastq extracted_reads")

@task
def assemble_reads():
    for fq in os.listdir("extracted_reads"):
        basename = fq.split(".")[0] + ".velvet"
        run("velveth "+ basename + " " + str(K) + " -short -fastq extracted_reads/" + fq)
        run("velvetg "+ basename + "-cov_cutoff 3.0" )

@task
def get_ordering():
    for assembly in os.listdir("*.velvet"):
        pass
        #blast assembly against the mRNA    

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
    velvetg $BASENAME -exp_cov 2 
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
-It may be interesting to try and do the entire thing in parallel. That is, it may be more efficient to launch n-processes for each gene instead of just letting them all go at once. Or even just using threads. That actually might be best. It's stupidly parallel and is mostly going to be I/O bound anyway. 


-Quantify how much we improved the assembly by
-Figure out when to stop iterating.
-Add new reads to the previous set

ALSO NOTE:
    what we are doing is basically overlap graph but with a crazy process that does local assembly to improve the assembly
"""
