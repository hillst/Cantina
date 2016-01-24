import zlib
__updated__ = "2015-6-17"
__author__ = "Steven Hill"
__version__ = "v0.1"
program_license = "Copyright 2015 Steven Hill Hendrix Lab Oregon State University     \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"


"""
The purpose of this program is to build a fast lookup for fastq file. Every block_size_t bytes represents one read with the following format:
read_id,position[PADDING]\n

TODO:
    Might be useful to use huffman encoding for the read-ids so we can minimize the block size.
"""
def build_index(fastq, index_name, block_size_t = 96, sort_data=True):
    output = open(index_name, 'w')
    byte_offset = block_size_t
    line_count = 0
    file_pos = 0
    entries = []
    fd = open(fastq, 'r')

    #we must use while true for constructing the index so our file pointer isnt messed up
    while True:
        line = fd.readline()
        if not line:
            break
        if line_count % 4 == 0:
            out_string = line.strip() + "," + str(file_pos)
            if byte_offset < 0:
                raise Exception("Cannot have a negative byte offset. Please increase the block size.")
            entries.append(out_string)
        elif line_count % 4 == 3:
            file_pos = fd.tell()

        line_count += 1
    if sort_data:
        entries.sort()
    for entry in entries:
        byte_offset = block_size_t - (len(entry)+1)
        print >> output, entry + (byte_offset * "\0")

    output.close()


def sort_index(index_name):
    entries = []
    for line in open(index_name, 'r'):
        entries.append(line)
    entries.sort()


def parse_entry(entry):
    return int(entry.split(",")[1].strip().strip("\0"))


def parse_name(entry):
    return entry.split(",")[0].strip()


def load_index_memory(index_name):
    index = {}
    for line in open(index_name, 'r'):
        index[parse_name(line)] = parse_entry(line)
    return index

