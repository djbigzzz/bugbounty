#!/bin/bash
# Quick ffuf directory fuzzing script
# Usage: ./ffuf-quick.sh https://target.com

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <target-url>"
    echo "Example: $0 https://example.com"
    exit 1
fi

TARGET="$1"
export PATH=$PATH:$HOME/go/bin

# Check if wordlist exists, if not download a basic one
WORDLIST="../wordlists/common.txt"

if [ ! -f "$WORDLIST" ]; then
    echo "[*] Downloading common wordlist..."
    curl -s https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -o "$WORDLIST" 2>/dev/null || {
        echo "[!] Could not download wordlist. Creating a basic one..."
        cat > "$WORDLIST" << 'EOF'
admin
api
backup
config
dashboard
debug
dev
docs
files
images
js
login
logout
manage
panel
phpinfo
private
public
robots.txt
sitemap.xml
static
status
swagger
test
upload
uploads
user
users
v1
v2
wp-admin
wp-content
.env
.git
.htaccess
.svn
EOF
    }
fi

echo "[*] Starting ffuf against: $TARGET"
echo "[*] Using wordlist: $WORDLIST"
echo ""

ffuf -u "${TARGET}/FUZZ" \
    -w "$WORDLIST" \
    -mc 200,201,204,301,302,307,401,403,405 \
    -fc 404 \
    -t 50 \
    -c

echo ""
echo "[*] Scan complete!"
