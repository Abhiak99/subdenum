import sys
import subdenum
if len(sys.argv) != 2:
	sys.exit()

f = open(sys.argv[1], "rt")
for subdomains in f:
	subdenum.subd(subdomains.strip())

f.close()
