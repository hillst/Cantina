# Cantina

Cantina is a transcript guided assembly pipeline. Instead of writing fresh assembly software, we exploit current assembly tools to perform local assembly around target transcripts. This allows for the assembler to focus on what is "important" and to ignore repetitive regions. Unfortunately, this will leave out things like pseudogenes and important regulatory regions of the genome which are not transcribed.


##TODO

### Pipeline development
- The sort and reorder portion is not automated yet, and I have no metric for evaluating gap closing, however my previous observations suggest it is not terrible to gap close after the first assembly stage.

- Restarting to the beginning of the pipeline is not automated. This may need to be controlled by a smarter process/class (maybe in tasks)

- There is no support for paired end reads. I believe we should be extremely strict about this. No /1 /2 format, perhaps only support interleaved reads, or vice versa.

- Refactor the getBlastHits.py program so the binary search is more universal

- The regular expression in the binary search for the ID line provides no guarantees.

- Evaluate the performance of different threads for the I/O process (finding reads).

### Evaluation

QUALITY:
The gene contained in the first scaffold of the 12-12 assembly is broken. It's a good target for evaluation. Simarly we should find genes in the shinsuwase assembly.
That gene is:
scaffold49204 Locus_130459_2 52.9 COMPLEX
This gene is probably a really good candidate for evaluating our assembly method. If we can get a contig nearly as large as the original then we have something pretty solid.

QUANTITY:
How many genes are assembled? What about the genes that didn't assemble? Are the complete? What's the N50? Do they scaffold together?

VERSITILITY:
Does it work on maize? Does it work on Norway Spruce? Arabidopsis?

## Requirements
Invoke python library, it also has some expectations about run directories so I'd take a look at tasks.py to make sure everything is configured.
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

