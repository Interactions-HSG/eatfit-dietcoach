#!/bin/bash
srcdir=/home/bam_test_user
target=https://us-central1-better-me-27592.cloudfunctions.net/pushUserData
inotifywait -m -e close_write "$srcdir" |
while read path eventlist eventfile
do
  unzip -p "$srcdir/$eventfile" | curl -X POST $target -d @- --header "Content-Type: application/json"
  rm "$srcdir/$eventfile"
done    
