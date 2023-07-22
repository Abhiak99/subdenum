import sys
if len(sys.argv)!=2:
	print("[*] Please provide the csv file ")
	print("[*] Usage : python3 {} (csvfile.csv)".format(sys.argv[0]))

def change(line):
	columns = line.split(',')
	if "URL" in columns or "DOMAIN" in columns or "WILDCARD" in columns:
		if(columns[3]=='true' and columns[4]=='true'):#Bounty | Inscope
		#if(columns[3]=='false' and columns[4]=='true'):#VDP | Inscope
			return columns[0]
			# print(columns[0],columns[1])


with open("download_csv.csv", "rt") as csvfile, open("target_scope.txt", "wt") as target:
	lines = csvfile.readlines()
	for line in lines:
		k = change(line)
		if k!=None:
			target.write(str(k).strip("http://*.")+"\n")
