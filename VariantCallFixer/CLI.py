"""*DEPRECATED*"""

import argparse
import re

import VariantCallFixer.Globals as Globals
from VariantCallFixer.ReadVCF import ReadVCF
from VariantCallFixer.CreateVCF import CreateVCF

varSplitter = re.compile("(?<Var>[A-za-z0-9]+)((?<Operand>[=><]+)(?<Assertion>[^\t \n:;])[:;]?)?")
def parseKeyValuePair(string):
    return varSplitter.match(string).groupdict()

def createParser():
    parser = argparse.ArgumentParser(prog="VariantCallFixer")

    parser.add_argument("action", choices=["create", "read"], type=lambda arg: arg.lower(), help="Not case-sensitive")

    with (readGroup := parser.add_argument_group("Read-arguments")):
        readGroup.add_argument("files", nargs="+", type=str)
        readGroup.add_argument("target", choices=["header", "where"], type=lambda arg: arg.lower(), help="Not case-sensitive")
        
        with (headerGroup := readGroup.add_argument_group("Find in Header")):
            headerGroup.add_argument("field", nargs="+", help="Name(s) of the field(s) to get.")
        
        with (entryGroup := readGroup.add_argument_group("Find Entries")):
            entryGroup.add_argument("--chrom", metavar="chrom", nargs="+", type=str)
            entryGroup.add_argument("--pos", metavar="pos", nargs="+", type=int)
            entryGroup.add_argument("--id", metavar="id", nargs="+", type=str)
            entryGroup.add_argument("--ref", metavar="ref", nargs="+", type=str)
            entryGroup.add_argument("--alt", metavar="alt", nargs="+", type=str)
            entryGroup.add_argument("--qual", metavar="qual", nargs="+", type=int)
            entryGroup.add_argument("--info", metavar="info", nargs="+", type=parseKeyValuePair)
            entryGroup.add_argument("--format", metavar="format", nargs="+", type=parseKeyValuePair, help="If no sample is specified through \"--samples\" then any samples matching the condition are grabbed. To only match when ALL samples match the condition, supply the optional flag \"--all\" as well.")
            entryGroup.add_argument("--samples", metavar="samples", nargs="+", type=str)
            
        readGroup.add_argument("--output", type=str)
        readGroup.add_argument("--sort-by-file", metavar="sortByFile", action="store_true", type=str)

    with (createGroup := parser.add_argument_group("Create-arguments")):
        createGroup.add_argument("file")
        createGroup.add_argument("-r", "--ref", "--reference", metavar="refPath", type=str)
    parser.add_argument("--version", metavar="version", action="store_true")
    
    return parser

def main():
    import sys
    parser = createParser()
    
    args = parser.parse_args(sys.argv)

    if args.version:
        print(Globals.__version__)
        exit()
    
    if "output" in args:
        OUT = args.output
    else:
        OUT = sys.stdout

    if args.action == "read":
        files : list[ReadVCF]= []
        for path in args.files:
            files.append(ReadVCF(path))
        
        if args.target == "head":
            for vcf in files:
                print(vcf.filename, out=OUT)
                for f in args.field:
                    print(vcf.header[f], out=OUT)
        else: # args.target == "where"
            if args.sortByFile:
                for vcf in files:
                    print(vcf.filename, out=OUT)
                    for row in vcf.where(CHROM=args.chrom, POS=args.pos, REF=args.ref, ALT=args.alt, QUAL=args.qual, FILTER=args.filter, INFO=args.info, FORMAT=args.format, rawOut=True):
                        print(row, out=OUT)
            else:
                rows = []
                for vcf in files:
                    for row in vcf.where(CHROM=args.chrom, POS=args.pos, REF=args.ref, ALT=args.alt, QUAL=args.qual, FILTER=args.filter, INFO=args.info, FORMAT=args.format, rawOut=True):
                        rows.append(row)
                rows.sort(key=lambda string:string.split("\t")[1])
                for row in rows:
                    print(row, out=OUT)
    
    else: # args.action == "create":
        if "file" in args:
            vcf = CreateVCF(args.file, args.refPath)
            vcf.close()
    
    return 0