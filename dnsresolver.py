from subprocess import run,PIPE
import sys



if len(sys.argv)!=3:
	print("[*] Usage: python3 {} subdomains_file_to_resolve output_filename".format(sys.argv[0]))
	sys.exit()


def resolver_check(filename):
	resolved_base = run(["dnsx","-l",filename,"-silent"],stdout=PIPE, stderr=PIPE, text=True, shell=False)
	return resolved_base.stdout

#File Input#

file = sys.argv[1]

#File Output#

outfile = sys.argv[2]

with open(outfile, "wt") as ofile:
	for i in resolver_check(file).splitlines():
		ofile.write(i+"\n")
	

# print(resolver_check(file))
