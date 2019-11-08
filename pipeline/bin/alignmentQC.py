#!/usr/bin/env python
# Copyright (C) 2013 Ion Torrent Systems, Inc. All Rights Reserved

import traceback
import os
import sys
import subprocess
import datetime
import multiprocessing
import ion
from optparse import OptionParser


def execute_output(cmd):
    try:
        process = subprocess.Popen(
            cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True
        )
        return process.communicate()[0]
    except Exception:
        traceback.print_exc()
        return ""


def getIndexVersion(aligner):
    try:
        if aligner == "tmap":
            command = "tmap index --version"
            return execute_output(command).strip()
        elif aligner == "bowtie2":
            return "bowtie2"
        else:
            return None
    except Exception:
        sys.stderr.write(
            "%s: ERROR: Problem encountered determining tmap format version\n"
            % sys.argv[0]
        )
        exit(1)


#    (refDir,refInfo,refFasta,infoFile) = findReference(options.genome_path, options.genome, options.aligner, index_version)


def findReference(genomePath, genome, aligner, indexVersion):

    if not genomePath:
        sys.stderr.write(
            "%s: ERROR:  no base paths defined to search for reference library\n"
            % sys.argv[0]
        )
        exit(1)

    if not genome:
        sys.stderr.write("%s: ERROR: Option --genome is required\n" % sys.argv[0])
        exit(1)

    dirName = indexVersion + "/" + genome
    found = 0
    refLocation = None
    for baseDir in genomePath.split(":"):
        refLocation = baseDir + "/" + dirName
        if os.path.exists(refLocation):
            found = 1
            break

    if not found:
        sys.stderr.write(
            "%s: ERROR: unable to find reference genome %s\n" % (sys.argv[0], genome)
        )
        sys.stderr.write(
            "%s: ERROR:  - Searched in the following locations: \n" % sys.argv[0]
        )
        for baseDir in genomePath.split(":"):
            refLocation = baseDir + "/" + dirName
            sys.stderr.write("%s: ERROR:  - %s \n" % (sys.argv[0], refLocation))
        exit(1)

    if aligner == "tmap":
        fastaFile = refLocation + "/" + genome + ".fasta"
    elif aligner == "bowtie2":
        fastaFile = refLocation + "/" + genome
    else:
        sys.stderr.write("%s: ERROR: unknown aligner %s\n" % (sys.argv[0], aligner))
        exit(1)

    if aligner == "tmap":
        if not os.path.exists(fastaFile):
            sys.stderr.write(
                "%s: ERROR:  unable to find reference fasta file %s\n"
                % (sys.argv[0], fastaFile)
            )
            exit(1)

    return (refLocation, "", fastaFile, "")


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option(
        "-i", "--input", help="Unmapped BAM file to be processed", dest="readFile"
    )
    parser.add_option("-g", "--genome", help="Genome name", dest="genome")
    parser.add_option(
        "-o",
        "--out-base-name",
        help="Base name for the output file",
        dest="out_base_name",
    )
    parser.add_option("-s", "--start-slop", help="Obsolete", dest="start_slop")
    parser.add_option("-n", "--sample-size", help="Obsolete", dest="sample_size")
    parser.add_option("-l", "--filter-length", help="Obsolete", dest="filter_length")
    parser.add_option(
        "-m", "--max-plot-read-len", help="Obsolete", dest="max_plot_read_len"
    )
    parser.add_option("-q", "--qscores", help="Obsolete", dest="qscores")
    parser.add_option(
        "-b",
        "--threads",
        help="Number of tmap threads",
        dest="threads",
        type="int",
        default=multiprocessing.cpu_count(),
    )
    parser.add_option(
        "-k", "--server-key", help="Server key for tmap", dest="server_key"
    )
    parser.add_option("-d", "--aligner", help="Aligner", dest="aligner", default="tmap")
    parser.add_option("--aligner-opts-rg", help="??", dest="aligner_opts_rg")
    parser.add_option(
        "--aligner-opts-extra",
        help="??",
        dest="aligner_opts_extra",
        default="stage1 map4",
    )
    parser.add_option("--aligner-opts-pairing", help="??", dest="aligner_opts_pairing")
    parser.add_option(
        "--mark-duplicates",
        help="??",
        dest="mark_duplicates",
        action="store_true",
        default=False,
    )
    parser.add_option(
        "--bidirectional",
        help="??",
        dest="bidirectional",
        action="store_true",
        default=False,
    )
    parser.add_option(
        "--indexing", help="??", dest="indexing", action="store_true", default=False
    )
    parser.add_option(
        "--skip-sorting",
        help="??",
        dest="skip_sorting",
        action="store_true",
        default=False,
    )
    parser.add_option(
        "-c",
        "--align-all-reads",
        help="??",
        dest="align_all_reads",
        action="store_true",
        default=False,
    )
    parser.add_option(
        "-a",
        "--genome-path",
        help="??",
        dest="genome_path",
        default="/referenceLibrary:/results/referenceLibrary:/opt/ion/referenceLibrary",
    )
    parser.add_option(
        "-p",
        "--sam-parsed",
        help="??",
        dest="sam_parsed",
        action="store_true",
        default=False,
    )
    parser.add_option(
        "--realign",
        help="Enable realignment",
        dest="realign",
        action="store_true",
        default=False,
    )
    parser.add_option(
        "--aligner-format-version",
        help="aligner format version e.g. tmap-f3",
        dest="aligner_format_version",
    )
    parser.add_option("--output-dir", help="??", dest="output_dir", default=".")
    parser.add_option(
        "--logfile", help="??", dest="logfile", default="alignmentQC_out.txt"
    )

    (options, args) = parser.parse_args()

    # Warnings
    if options.aligner_opts_pairing is not None:
        sys.stderr.write(
            "%s: WARNING: --aligner-opts-pairing is not implemented. Only processing one file\n"
            % sys.argv[0]
        )
    if options.start_slop is not None:
        sys.stderr.write(
            "%s: WARNING: --start-slop is obsolete: Never run alignStats\n"
            % sys.argv[0]
        )
    if options.filter_length is not None:
        sys.stderr.write(
            "%s: WARNING: --filter-length is obsolete: Never run alignStats\n"
            % sys.argv[0]
        )
    if options.max_plot_read_len is not None:
        sys.stderr.write(
            "%s: WARNING: --max-plot-read-len is obsolete: Never run alignStats\n"
            % sys.argv[0]
        )
    if options.qscores is not None:
        sys.stderr.write(
            "%s: WARNING: --qscores is obsolete: Never run alignStats\n" % sys.argv[0]
        )
    if options.sample_size is not None:
        sys.stderr.write(
            "%s: WARNING: --sample-size is obsolete: Always align all reads\n"
            % sys.argv[0]
        )
    if options.align_all_reads:
        sys.stderr.write(
            "%s: WARNING: --align-all-reads is obsolete: Always align all reads\n"
            % sys.argv[0]
        )
    if options.sam_parsed:
        sys.stderr.write(
            "%s: WARNING: --sam-parsed is obsolete: Never generate SAM.parsed\n"
            % sys.argv[0]
        )

    if options.threads < 1:
        sys.stderr.write(
            "%s: ERROR: must specify a positive number of threads\n" % sys.argv[0]
        )
        exit(1)

    if not options.readFile:
        sys.stderr.write("%s: ERROR: Option --input is required\n" % sys.argv[0])
        exit(1)

    if options.readFile.endswith(".fasta"):
        readFileType = "fasta"
        readFileBase = options.readFile[:-6]
    elif options.readFile.endswith(".fastq"):
        readFileType = "fastq"
        readFileBase = options.readFile[:-6]
    elif options.readFile.endswith(".sff"):
        readFileType = "sff"
        readFileBase = options.readFile[:-6]
    elif options.readFile.endswith(".basecaller.bam"):
        readFileType = "bam"
        readFileBase = options.readFile[:-15]
    else:
        sys.stderr.write(
            "%s: ERROR: suffix of input reads filename %s should be one of (.fasta, .fastq, .sff, .basecaller.bam)\n"
            % (sys.argv[0], options.readFile)
        )
        exit(1)

    if os.path.exists(options.logfile):
        os.unlink(options.logfile)

    # Find the location of the genome index
    if options.aligner_format_version:
        index_version = options.aligner_format_version
    else:
        index_version = getIndexVersion(options.aligner)

    (refDir, refInfo, refFasta, infoFile) = findReference(
        options.genome_path, options.genome, options.aligner, index_version
    )

    print("Aligning to reference genome in " + str(refDir))

    # If out base name was not specified then derive from the base name of the input file
    if not options.out_base_name:
        options.out_base_name = readFileBase

    bamBase = options.output_dir + "/" + options.out_base_name
    bamFile = bamBase + ".bam"
    alignStartTime = datetime.datetime.now()

    if options.aligner == "tmap":
        command = "tmap mapall"
        command += " -n %d" % options.threads
        if options.server_key:
            command += " -k %s" % options.server_key
        else:
            command += " -f %s" % refFasta

        command += " -r %s" % options.readFile
        command += " -v"
        command += " -Y"
        if options.bidirectional:
            command += " --bidirectional"
        if options.realign:
            command += " --do-realign"
        if options.aligner_opts_rg:
            command += " " + options.aligner_opts_rg
        command += (
            " -u --prefix-exclude 5"
        )  # random seed based on read name after ignoring first 5 characters
        command += " -o 2"  # -o 0: SAM, -o 2: uncomp BAM
        command += " " + options.aligner_opts_extra
        command += " 2>> " + options.logfile
    elif options.aligner == "bowtie2":
        fastqpipe = bamBase + ".fastqfifo"
        command = "java -Xmx8g -jar %s SamToFastq I=%s F=%s" % (
            ion.picardPath,
            options.readFile,
            fastqpipe,
        )
        command += " | /results/plugins/bowtielauncher/bowtie2 -p%d -x %s -U %s" % (
            options.threads,
            refFasta,
            fastqpipe,
        )
        command += " | samtools view -ubS -"
    else:
        print("unknown aligner '%s'" % options.aligner)
        sys.exit(1)

    if not options.skip_sorting:
        # bug same as in http://abrt.fedoraproject.org/faf/problems/932874/
        # command += " | samtools sort -m 12G -l1 -@%d -" % options.threads
        command += " | samtools sort -m 2G -l1 -@3 -"
    else:
        command += " >"

    if options.mark_duplicates:
        command += " %s.tmp" % bamBase
    else:
        command += " %s" % bamBase

    if options.skip_sorting:
        command += ".bam"

    if options.aligner == "bowtie2":
        makepipe_cmd = "mkfifo %s" % (fastqpipe)
        print(makepipe_cmd)
        subprocess.call(makepipe_cmd, shell=True)

    print(command)
    subprocess.call(command, shell=True)

    # cleanup
    if options.aligner == "bowtie2":
        rmpipe_cmd = "rm %s" % (fastqpipe)
        print(rmpipe_cmd)
        subprocess.call(rmpipe_cmd, shell=True)

    if options.mark_duplicates:
        command = "BamDuplicates"
        json_name = (
            ("BamDuplicates.%s.json") % (os.path.normpath(options.out_base_name))
            if os.path.normpath(options.out_base_name) != "rawlib"
            else "BamDuplicates.json"
        )
        command += " -i %s.tmp.bam" % bamBase
        command += " -o %s -j %s" % (bamFile, json_name)
        print(command)
        subprocess.call(command, shell=True)
        command = "rm -v %s.tmp.bam" % bamBase
        print(command)
        subprocess.call(command, shell=True)

    if options.indexing and not options.skip_sorting:
        command = "samtools index " + bamFile
        print(command)
        subprocess.call(command, shell=True)

    alignStopTime = datetime.datetime.now()
    alignTime = (alignStopTime - alignStartTime).seconds
    print("Alignment time: %d:%02d minutes" % (alignTime / 60, alignTime % 60))
