#!/usr/bin/env python
import operator
import sys

CHAR_P_LINE=80
NUM_N = 3

def main():
    if len(sys.argv) < 3 or "--help" in sys.argv or "-h" in sys.argv: 
        printUsage()
        sys.exit()
    contigs = sys.argv[1]
    blast_hits = sys.argv[2]
    order, rev_comp = orderScaffolds(blast_hits)
    reads = mergeScaffolds(contigs)    
    printHits(reads, order, rev_comp)

def printHits(reads, order, rev_comp):
    print ">MERGED_ORDERED_SCAFFOLDS"
    for hit in order:
        #check for reversal
        if hit in rev_comp:
            to_print = revcom(reads[hit])
        else:
            to_print = reads[hit]
        remainder = 0
        #print by block
        i = 0
        for i in range(0,len(to_print), CHAR_P_LINE):
            if i + CHAR_P_LINE < len(to_print):
                print to_print[i:i+CHAR_P_LINE]
        #set N's
        remainder = CHAR_P_LINE - (len(to_print) -  i) 
        print to_print[i:i+CHAR_P_LINE] + "N" * remainder
        for i in range(NUM_N):
            print "N" * CHAR_P_LINE

def printUsage():
    print >> sys.stderr, "orderScaffolds.py\t<contigs.fa>\t<blast_hits.txt>"
    print >> sys.stderr, "Expects the contigs.fa file from velvet and blast hits file output with outfmt 6"
    print >> sys.stderr, ""
    print >> sys.stderr, "Result will be a new output of concatenated, ordered scaffolds."


def complement(s): 
    basecomplement = {'A':'T','C':'G','G':'C','T':'A','a':'t','t':'a','c':'g','g':'c','N':'N'} 
    letters = list(s) 
    letters = [basecomplement[base] for base in letters] 
    return ''.join(letters)


def revcom(s):
    return complement(s[::-1])


def orderScaffolds(blast_hits):
    fd = open(blast_hits, 'r')
    order = {}
    contigs = {}
    rev_comp = {}
    for line in fd:
        query, target, identity, length, mismatches, gapopens, startq, stopq, startt, endt,evalue, bitscore = line.strip().split("\t")
        if int(startt) < int(endt):
            order[query] = int(startt)
        else:
            order[query] = int(endt)
            rev_comp[query] = True
        if query not in contigs:
            contigs[query] = [line]
        else:
            contigs[query].append(line)
    sorted_order = sorted(order.keys(), key=order.__getitem__)
    return sorted_order, rev_comp

def mergeScaffolds(contigs):
    numNs = 200
    fd = open(contigs,'r')
    reads = {} #id => lines
    buffer = []
    header = ""

    for line in fd:
        if ">" in line[0]:
            if len(buffer) == 0:
                header = line.strip()[1:]
                continue
            else:
                reads[header] = ""
                
                for seq in buffer:
                    reads[header] += seq.strip()
                buffer = []
                header = line.strip()[1:]
        elif ">" not in line[0]:
            buffer.append(line)
    #one last time
    reads[header] = ""
    for seq in buffer:
        reads[header] += seq.strip()
    return reads


if __name__ == "__main__":
    main()
