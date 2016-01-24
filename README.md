# Cantina

Cantina is a transcript guided assembly pipeline. Instead of writing fresh assembly software, we exploit current assembly tools to perform local assembly around target transcripts. This allows for the assembler to focus on what is "important" and to ignore repetitive regions. Unfortunately, this will leave out things like pseudogenes and important regulatory regions of the genome which are not transcribed.



## Requirements
Invoke python library, it also has some expectations about run directories so I'd take a look at tasks.py to make sure everything is configured.
FastqIndex python library. You can get this here:
    
    git@github.com:hillst/FastqIndex.git


Also expectes velvet (version not listed yet), and the ncbi-blastn

## Running
to run, simply type:
inv -l
to get a list of command
The pipeline should go as follows:
sort reads/create blastdb of reads
blast contigs to reads
extract reads from blast hits
assemble reads
order reads
repeat (not done yet)

