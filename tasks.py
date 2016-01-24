#!/home/pi/hillst/.local/bin/inv
from invoke import task, run
import os
"""
We are allowed to make a set of assumptions, much like make, and treat them as global variables

Assumptions 
1) Files in wgs_reads have the same name prefix as the blast databases
2) Indexes produced by FastqIndex have the same prefix as the fastq files. 
3) No "pipe" ( | ) symbols in fasta header names
"""
TARGETS="targets.fa"
BLASTN="blastn"
THREADS="8"
num_jobs=8
MAX_READS="2000" # A smaller number will result in a "worse" assembly but in faster runtime. It may not be necessary to have more than a couple of hundred for this parmaeter
GET_READS="~/bin/Cantina/bin/getBlastRawReads.py"
K="31"
ITERATIONS=3

@task(help={"files":"Runs the full pipeline on the passed fastq files. It's important to note that in order to use wildcard dilemeters you MUST surround them with quotes."})
def all():
    run("echo 'hello from build'")

@task
def pipeline():
    for i in range(ITERATIONS):
        if i == 0:
            target = TARGETS
        clean_up_extracted_reads()
        blast_all(target)
        extract_reads()
        assemble_reads()
        get_ordering()
        gap_close()
        target = gather_scaffolds(str(i))
        backup_velvet(str(i))

@task
def clean(all=False):
    if all:
        run("rm -rf blastdb")
        run("rm -rf wgs_reads")
    run("rm -rf *.velvet")
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
    
@task(help={"target":"File containing the contigs that we are searching for."})
def blast_all(target=TARGETS):
    print "running blast", target
    from multiprocessing import Pool
    p = Pool(num_jobs)
    databases = set([".".join(thing.split(".")[:-1]) for thing in os.listdir("blastdb") if ".nal" in thing])
    commands = []
    for database in databases:
        if database != "targets":
            commands.append(BLASTN + " " + "-num_threads " + THREADS + " -query " + target + " -db blastdb/" + database + " -max_target_seqs " + MAX_READS + " -outfmt 6 > blast_results/" + database + ".blastn")
    p.map(run, commands) 

def blast_command_helper(command):
    return 

@task
def extract_reads():
    print "extracting reads"
    for result in os.listdir("blast_results"):
        basename = ".".join(result.split(".")[:-1])
        run("python " + GET_READS + " -b blast_results/"+result + " -r wgs_reads/" + basename +".fastq" + " -t 8")
    run("mv *.fastq extracted_reads")

@task
def assemble_reads():
    for fq in os.listdir("extracted_reads"):
        basename = ".".join(fq.split(".")[:-1]) + ".velvet"
        try:
            run("velveth "+ basename + " " + str(K) + " -short -fastq extracted_reads/" + fq)
            run("velvetg "+ basename + " -exp_cov auto" )
        except Exception as e:
            print "WARNING", basename, "FAILED TO ASSEMBLE"

@task
def get_ordering():
    count = 0
    print "getting order"
    to_get = len([ folder for folder in os.listdir(".") if ".velvet" in folder])
    suspect = []
    for assembly in [ folder for folder in os.listdir(".") if ".velvet" in folder]:
        basename = ".".join(assembly.split(".")[:-1])
        try:
            dicks = run("blastn -query " + assembly +"/contigs.fa " + "-db mRNA_blast/mRNA " + " -outfmt 6 | grep " + basename + " > " + assembly + "/contigs.blastn")
            run("python orderContigs.py " + assembly + "/contigs.fa " + assembly + "/contigs.blastn > " + assembly + "/contigs.ordered.fa")
        except Exception as e:
            print "WARNING:", basename, "is empty!!! It is being added to the list of suspcious mRNAs."
            suspect.append(basename)
        #run("exonerate --model est2genome --query targets.fa --target "+ assembly+"/contigs.ordered.fa > " +assembly +"/exonerate.txt") 
        count += 1
        #print float(count)/to_get, "%\r",
    print ""
        #blast assembly against the mRNA    

@task
def gap_close():
    print "gap closing"
    count = 0
    to_get = len([ folder for folder in os.listdir(".") if ".velvet" in folder])
    for assembly in [ folder for folder in os.listdir(".") if ".velvet" in folder]:
        basename = ".".join(assembly.split(".")[:-1])
        try:
            generate_gapclose_config(basename)
            print assembly + "/gapcloser.config"
            run("~/bin/GapCloser -a " + assembly + "/contigs.ordered.fa -b " + assembly + "/gapcloser.config -o "+ assembly +"/contigs.ordered.filled.fa -l 200 -p 20 -t " + THREADS) 
        except Exception as e:
            pass
        #run("exonerate --model est2genome --query targets.fa --target "+ assembly+"/contigs.ordered.filled.fa > " +assembly +"/exonerate.filled.txt") 
        count += 1
        print float(count)/to_get, "%\r",
    print ""

"""
Moving them is another option
"""
@task
def clean_up_extracted_reads():
    run("rm -f extracted_reads/*")

@task
def gather_scaffolds(step="1"):
    for assembly in [ folder for folder in os.listdir(".") if ".velvet" in folder]:
        try:
            run("cat " + assembly + "/contigs.ordered.filled.fa >> targets_round"+step+".fa")
        except Exception as e:
            pass
    return "targets_round"+step+".fa"

@task
def backup_velvet(step="1"): 
    for assembly in [ folder for folder in os.listdir(".") if ".velvet" in folder]:
        run("cp " + assembly + "/contigs.ordered.filled.fa " + assembly + "/contigs.ordered.filled." + step + ".fa")

def generate_gapclose_config(transcript):
    with open(transcript + ".velvet/gapcloser.config", 'w') as fd:
        print >> fd, "[LIB]"
        print >> fd, "asm_flags=4"
        print >> fd, "rank=1"
        print >> fd, "q=extracted_reads/"+transcript+".fastq"
    
