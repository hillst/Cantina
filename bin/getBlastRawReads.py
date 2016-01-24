#!/usr/bin/env python
import re
'''
program name -- getBlastRawReads
program name -- getBlastRawReads
@author:     Steven Hill
@copyright:  2014 Hendrix Lab Oregon State University. All rights reserved.
@contact:    hillst@onid.oregonstate.edu
'''

__author__ = 'Hill'

import sys
import os
from optparse import OptionParser
from fastq_lookup import *
__all__ = []
__version__ = 0.1
__date__ = '2014-11-24'
__updated__ = '2014-11-24'


def main():
    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_license = "Copyright 2014 Steven Hill Hendrix Lab Oregon State University     \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"
    program_longdesc = "Takes tabular blast output and fetches the raw reads from a paired fastq file. Supports interleaved paired end reads. Expects an index to be present that has the same prefix as the fastq file."

    argv = sys.argv[1:]
        # setup option parser
    parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
    parser.add_option("-b", "--blast", dest="blast", help="Tabular output from BLAST to a blastdb of raw reads.", metavar="FILE")
    parser.add_option("-t", "--num-threads", dest="num_threads", help="Number of threads to use when searching for reads.", metavar="INT")
    parser.add_option("-r", "--raw-reads", dest="reads", help="A single fastq file containing the source reads. If the reads are paired they should be interleaved.", metavar="FILE")
    # process options
    (opts, args) = parser.parse_args(argv)
    blast, rawReads, num_threads = opts.blast, opts.reads, int(opts.num_threads)

    if num_threads is None:
        num_threads = 1
    if blast is None or rawReads is None:
        parser.print_usage()
        sys.exit(-1)
    # MAIN BODY #
    toFind = {}
    print >> sys.stderr, "reading blast hits", "\r",
    readBlast(blast, toFind)
    print >> sys.stderr, "finding reads", "\r",
    findReads(rawReads, toFind, num_threads)


def readBlast(blast, toFind):
    """
    probably read the blast file in here, build a dictionary of sequence names to go get. Instead of doing filtering
    we can require the user to do their own filtering (should be good enough)

    gi|407317192|gb|JQ063073.1|     DB775P1:292:D291PACXX:1:2308:14191:63215        100.00  101     0       0       254     354     101     1       4e-44     187
    :return:
    """
    fd = open(blast, 'r')
    for line in fd:
        query, target, identity, length, mismatches, gapopens, startq, stopq, startt, endt,evalue, bitscore = line.strip().split("\t")
        target = "@" + target #TODO specific to blast format, honestly this should be more normalized somehow. Maybe at the index level since @ is a fastq delimeter
        if query not in toFind:
            toFind[query] = {}
        toFind[query][target] = line
    return toFind

def fastqIndexLookup(args):
    to_find, lookup = args
    return lookup.find_entry(to_find)

"""
expects a given fastq file to be sorted
"""
def fastqBinarySearch(args):
    to_find, file = args 
    with open(file, 'r') as fp:
        begin = 0
        fp.seek(0, 2)
        end = fp.tell()
        previous = 0
        history = []
        lines = []
        iterations = 0
        while (begin < end):
            fp.seek(begin + (end - begin) / 2, 0)
            new_spot = fp.tell()
            #split 0 is a technicality that removes the weird mulitplexing information, could encode this in a regex
            line = fp.readline()
            if " " in line:
                line = line.split()[0]
            header_match = re.search(r'^@[A-Za-z0-9_.-]+:[\d]+:[A-Za-z0-9-]+:[\d]+:[\d]+:[\d]+:[\d]+$', line) 
            finding_header = 0

            while header_match == None:
                line = fp.readline()
                if " " in line:
                    line = line.split()[0]
                line_key = line.strip()[1:]
                #TODO This regular expression is by NO means comprehensive. We may need a fallback expression or a way to excape this.
                header_match = re.search(r'^@[A-Za-z0-9_.-]+:[\d]+:[A-Za-z0-9-]+:[\d]+:[\d]+:[\d]+:[\d]+$', line) 
                finding_header += 1
            #take a large jump
            if fp.tell() == previous:
                fp.seek(0)
            if (to_find == line_key):
                lines.append(line)
                for line in range(3):
                    lines.append(fp.readline())
                #print  "found", to_find, iterations, "iterations"
                return lines
            elif (to_find > line_key):
                begin = fp.tell()
            else:
                end = fp.tell()
            if iterations > 100:
                raise SearchException("probably stuck")
            previous = fp.tell()
            iterations += 1
        if len(lines) == 0:
            pass
            #print "failed to find", to_find, iterations, begin, end, previous, finding_header
        return lines

def findReads(reads, toFind, num_threads):
    file_streams = {}
    index = reads.replace(".fastq", ".index")
    #hack
    lookup = BinaryLookup(index, reads)
    from multiprocessing import Pool
    p = Pool(num_threads)
    for query in toFind:
        count = 0
        file_streams[query] = open(query.replace("|","_") + ".fastq", 'wa')
        print >> sys.stdout, "Searching for:", len(toFind[query]), query
        output = file_streams[query]
        print output
        for result in map(fastqIndexLookup, [ (val,lookup) for val in toFind[query]]):
            for line in result:
                print >> output, line.strip()
        print ""
        output.close()

class SearchException(Exception):
    def __init__(self, msg):
        Exception.__init__(self,msg)

if __name__ == '__main__':
    main()
