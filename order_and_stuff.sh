echo "determining order of contigs"
blastn -db mRNA_blastdb/targets -query gi_146229452_gb_ES437721.velvet//contigs.fa -outfmt 6 > gi_146229452_gb_ES437721.velvet.blastn
echo "ordering contigs"
python orderContigs.py gi_146229452_gb_ES437721.velvet/contigs.fa gi_146229452_gb_ES437721.velvet.blastn > gi_146229452_gb_ES437721.velvet///contigs.ordered.fa
echo "running exonerate"
exonerate --model est2genome --query targets.fa --target gi_146229452_gb_ES437721.velvet/contigs.ordered.fa
