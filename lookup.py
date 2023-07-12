from nslookup import Nslookup
import json
import sys
if len(sys.argv) != 2:
	print("[*] Usage python3 %s [subdomain.txt]" % sys.argv[0])
	sys.exit()
f = open(sys.argv[1], "rt")
ips = {}

for domain in f:
	dns_query = Nslookup(dns_servers=["8.8.8.8","1.1.1.1"], verbose=False, tcp=False)

	ips_record = dns_query.dns_lookup(domain.strip())
	# print(ips_record.response_full, ips_record.answer)

	if ips_record.answer:
            ips[domain.strip()]=ips_record.answer
f.close()


f = open("alivesubdomains.txt","w")
for i in ips.keys():
    f.write(i+"\n")
f.close()
y = json.dumps(ips)
print(y)
