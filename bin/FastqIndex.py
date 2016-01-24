#!/usr/bin/env python
import sys
import os

from optparse import OptionParser
import fastq_index
__updated__ = "2015-6-17"
__author__ = "Steven Hill"
"""
The purpose of this program is to build a fast lookup for fastq file. Every 128 bytes represents one read with the following format:
read_id,position[PADDING]\n
"""


def main():
    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_license = "Copyright 2015 Steven Hill Hendrix Lab Oregon State University     \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"
    program_longdesc = "The purpose of this program is to build a fast lookup for fastq file. Every 128 bytes represents\
                        one read with the following format:\n read_id,position[PADDING]\\n"

    argv = sys.argv[1:]
        # setup option parser
    parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
    parser.add_option("-f", "--fastq", dest="fastq", help="Fastq file to index", metavar="FILE")
    parser.add_option("-c", "--index-name", dest="index_name", help="Name of the resulting index", metavar="STRING")
    parser.add_option("-b", "--block-size", dest="block_size", help="Block size for each index entry\t[OPTIONAL]", metavar="INT")
    parser.add_option("-s", "--skip-sorting",  \
                    action="store_false", dest="sort_data", default=True,
                    help="Skip the sorting of the fastq read ids. Only use this if the fastq is already sorted.\t[OPTIONAL]", metavar="BOOL")
    # process options
    (opts, args) = parser.parse_args(argv)
    fastq, index_name = opts.fastq, opts.index_name
    if fastq is None or index_name is None:
        parser.print_help()
        sys.exit(-1)
    if not opts.block_size is None:
        fastq_index.build_index(fastq, index_name, int(opts.block_size), sort_data=opts.sort_data)
    else:
        fastq_index.build_index(fastq, index_name, sort_data=opts.sort_data)


if __name__ == "__main__":
    main()