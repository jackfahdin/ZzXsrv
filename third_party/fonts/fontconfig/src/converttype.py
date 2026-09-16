import sys,re

infile=open(sys.argv[1],"r")
inbuffer=infile.read()
infile.close()
outfile=open(sys.argv[1],"w")
inbuffer=re.sub(r'\(int\)\(long\)&\(',r'(int)(intptr_t)&(',inbuffer)
# gperf 3.0 emits unsigned int, while newer versions emit size_t. Match the
# production prototypes on both x86 and x64 without narrowing the call ABI.
inbuffer=re.sub(r'\b(?:unsigned int|size_t) len\b',r'FC_GPERF_SIZE_T len',inbuffer)
outfile.write(inbuffer)
outfile.close()

