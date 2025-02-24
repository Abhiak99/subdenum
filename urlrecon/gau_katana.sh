#!/bin/bash
# Usage: ./gau_katana_httpx.sh <subdomains_file>
# The input file should have one subdomain per line (e.g. sub.example.com or http://target)
# For each subdomain, the script will:
# 1. Run gau and katana -jc to gather URLs.
# 2. Combine, deduplicate and save them in a folder "raw_urls" with a sanitized file name.
# 3. Run httpx to check URL status codes and separate them into folders by status:
#    httpx_results/200, httpx_results/30x, httpx_results/40x, and httpx_results/50x.

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <subdomains_file>"
    exit 1
fi

input_file="$1"
if [ ! -f "$input_file" ]; then
    echo "File not found: $input_file"
    exit 1
fi

# Create directories to organize outputs
mkdir -p raw_urls
mkdir -p httpx_results/200 httpx_results/30x httpx_results/40x httpx_results/50x

# Read the subdomains into an array to avoid STDIN issues
mapfile -t subdomains < "$input_file"

for subdomain in "${subdomains[@]}"; do
    # Skip empty or commented lines
    [[ -z "$subdomain" || "$subdomain" =~ ^# ]] && continue

    echo "======================================"
    echo "[*] Processing subdomain: $subdomain"

    # Sanitize the subdomain for file naming:
    # 1. Remove http:// or https:// if present.
    # 2. Replace any character not alphanumeric, dot, dash, or underscore with underscore.
    safe_subdomain=$(echo "$subdomain" | sed 's|https\?://||; s/[^A-Za-z0-9._-]/_/g')
    
    raw_output_file="raw_urls/${safe_subdomain}.txt"
    
    # Create temporary files for gau and katana outputs
    gau_tmp=$(mktemp)
    katana_tmp=$(mktemp)
    
    echo "[*] Running gau for $subdomain..."
    gau "$subdomain" < /dev/null > "$gau_tmp"
    
    echo "[*] Running katana -jc for $subdomain..."
    # Use the -u flag so katana gets its target properly.
    katana -silent -jc -u "$subdomain" < /dev/null > "$katana_tmp"
    
    echo "[*] Combining and deduplicating URLs..."
    cat "$gau_tmp" "$katana_tmp" | sort -u > "$raw_output_file"
    
    # Clean up temporary files
    rm "$gau_tmp" "$katana_tmp"
    
    # Check if the raw output file has content
    if [ ! -s "$raw_output_file" ]; then
        echo "[-] No URLs found for $subdomain; skipping httpx check."
        rm -f "$raw_output_file"
        continue
    fi

    echo "[*] Running httpx on URLs from $subdomain..."
    httpx_tmp=$(mktemp)
    # Run httpx with silent mode and output status codes
    httpx -l "$raw_output_file" -silent -status-code > "$httpx_tmp"
    
    # Define output files for different status codes using the sanitized subdomain
    alive_file="httpx_results/200/${safe_subdomain}_alive.txt"
    _30x_file="httpx_results/30x/${safe_subdomain}_30x.txt"
    _40x_file="httpx_results/40x/${safe_subdomain}_40x.txt"
    _50x_file="httpx_results/50x/${safe_subdomain}_50x.txt"
    
    # Filter and save based on HTTP status code.
    # Assumes httpx output lines end with the status code (e.g. "https://example.com 200")
    grep -E "\s200$" "$httpx_tmp" > "$alive_file"
    grep -E "\s3[0-9][0-9]$" "$httpx_tmp" > "$_30x_file"
    grep -E "\s4[0-9][0-9]$" "$httpx_tmp" > "$_40x_file"
    grep -E "\s5[0-9][0-9]$" "$httpx_tmp" > "$_50x_file"
    
    # Clean up temporary httpx output file
    rm "$httpx_tmp"
    
    # Report and remove empty result files if no URLs matched
    if [ -s "$alive_file" ]; then
        echo "[+] Alive URLs (200) for $subdomain saved to $alive_file"
    else
        echo "[-] No alive URLs (200) found for $subdomain."
        rm -f "$alive_file"
    fi

    if [ -s "$_30x_file" ]; then
        echo "[+] 30x URLs for $subdomain saved to $_30x_file"
    else
        echo "[-] No 30x URLs found for $subdomain."
        rm -f "$_30x_file"
    fi

    if [ -s "$_40x_file" ]; then
        echo "[+] 40x URLs for $subdomain saved to $_40x_file"
    else
        echo "[-] No 40x URLs found for $subdomain."
        rm -f "$_40x_file"
    fi

    if [ -s "$_50x_file" ]; then
        echo "[+] 50x URLs for $subdomain saved to $_50x_file"
    else
        echo "[-] No 50x URLs found for $subdomain."
        rm -f "$_50x_file"
    fi
    
    echo "======================================"
    echo
done
