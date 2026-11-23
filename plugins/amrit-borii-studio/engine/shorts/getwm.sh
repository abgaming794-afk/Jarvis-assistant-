#!/bin/bash
# usage: getwm.sh "File name.jpg" width out.jpg
f="${1// /_}"; h=$(printf '%s' "$f" | md5sum | cut -c1-2); a=${h:0:1}
enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$f")
ext="${f##*.}"; suf=""; [ "$ext" = "gif" ] && suf=""; 
url="https://upload.wikimedia.org/wikipedia/commons/thumb/$a/$h/$enc/$2px-$enc"
[ "$ext" = "tif" ] && url="$url.jpg"
for i in 1 2 3 4 5 6; do curl -s -A "Mozilla/5.0 (compatible; research-script/1.0)" -o "$3" "$url"; if file "$3" | grep -qE "JPEG|PNG|GIF"; then echo "OK $3 $(file -b "$3" | cut -c1-60)"; return 0 2>/dev/null || exit 0; fi; c=$(head -c 200 "$3" | tr -d '\n' | cut -c1-80); echo "retry $i $3 ($c)"; sleep $((15*i)); done; echo "FAIL $3 $url"
