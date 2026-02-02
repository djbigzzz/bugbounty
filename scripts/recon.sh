#!/bin/bash
# Bug Bounty Recon Script
# Usage: ./recon.sh target.com

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <target-domain>"
    echo "Example: $0 example.com"
    exit 1
fi

TARGET="$1"
OUTPUT_DIR="../targets/$TARGET"
DATE=$(date +%Y%m%d_%H%M%S)

echo "[*] Starting recon for: $TARGET"
echo "[*] Output directory: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"/{subdomains,urls,screenshots,nuclei}

# Add Go binaries to PATH
export PATH=$PATH:$HOME/go/bin

# Step 1: Subdomain enumeration (if subfinder is available)
if command -v subfinder &> /dev/null; then
    echo "[+] Running subfinder..."
    subfinder -d "$TARGET" -o "$OUTPUT_DIR/subdomains/subfinder.txt" 2>/dev/null || true
fi

# Step 2: HTTP probing (if httpx is available)
if command -v httpx &> /dev/null && [ -f "$OUTPUT_DIR/subdomains/subfinder.txt" ]; then
    echo "[+] Running httpx..."
    httpx -l "$OUTPUT_DIR/subdomains/subfinder.txt" -o "$OUTPUT_DIR/urls/live_hosts.txt" 2>/dev/null || true
fi

# Step 3: Directory fuzzing with ffuf (if available)
if command -v ffuf &> /dev/null; then
    echo "[+] ffuf is available for directory fuzzing"
    echo "    Run manually: ffuf -u https://$TARGET/FUZZ -w /path/to/wordlist.txt"
fi

# Step 4: Nuclei scanning (if available)
if command -v nuclei &> /dev/null; then
    echo "[+] nuclei is available for vulnerability scanning"
    echo "    Run manually: nuclei -u https://$TARGET -o $OUTPUT_DIR/nuclei/results.txt"
fi

echo ""
echo "[*] Recon complete! Results saved to: $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "  1. Review discovered subdomains in $OUTPUT_DIR/subdomains/"
echo "  2. Run ffuf for directory discovery"
echo "  3. Start manual testing with Burp Suite"
