import fastq_index

__updated__ = "2015-6-17"
__author__ = "Steven Hill"
__version__ = "v0.1"
program_license = "Copyright 2015 Steven Hill Hendrix Lab Oregon State University     \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"


class Lookup:
    def __init__(self, index_name, fastq_name):
        self.fastq_name = fastq_name
        self.index_name = index_name

    def find_entry(self, entry, fastq):
        """
        :param entry: Entry to find
        :param fastq: Name of the fastq file
        :return: Four entry list containing the fastq read
        """
        raise NotImplemented("Cannot call a method from an interface.")

    def get_read(self, offset):
        """
        Fetches the reads starting at the passed offset
        :param offset: offset where the read begins
        :return: list of lines which belong to this read
        """
        reads = []
        with open(self.fastq_name, 'r') as fd:
            fd.seek(offset)
            for i in range(4):
                reads.append(fd.readline().strip())
        return reads

class BinaryLookup(Lookup):
    __name = "BinaryLookup"
    def __init__(self, index_name, fastq_name):
        Lookup.__init__(self, index_name, fastq_name)
        #impirically calculate block size
        fd = open(self.index_name, 'r')
        fd.readline()
        self.line_size = fd.tell()
        fd.close()

    def find_entry(self, entry):
        offset = self.binary_search(entry)
        return self.get_read(offset)


    def binary_search(self, key):
        """
        Finds the passed key and returns the byte offset it occurs in the index.
        :param key:
        :return:
        """
        with open(self.index_name, 'r') as fd:
            fd.seek(0, 2)
            max_byte = fd.tell() - self.line_size
            imin = 0
            imax = max_byte / self.line_size
            fd.seek(0)

            while (imax >= imin):
            #midpoint
                imid = self.midpoint(imin, imax)
                fd.seek(imid * self.line_size)
                entry = fd.readline()

                current = fastq_index.parse_name(entry)
                # Get's around the problem of BLAST truncating names I suppose. Not the best fix.
                if key in current:
                    return fastq_index.parse_entry(entry)
                elif current < key:
                    imin = imid + 1
                else:
                    imax = imid - 1
            return -1
    def midpoint(self, imin, imax):
        return imin + (imax - imin) / 2


class DictionaryLookup(Lookup):
    __name = "DictionaryLookup"
    def __init__(self, index_name, fastq_name):
        Lookup.__init__(self, index_name, fastq_name)
        self.index = fastq_index.load_index_memory(index_name)


    def find_entry(self, entry):
        offset = self.index[entry]
        if offset == -1:
            #maybe this should raise an exception?
            print >> sys.stderr, "ERROR: could not find entry", entry
        return self.get_read(offset)



