#!/bin/bash

rm -r notes
mkdir notes

cp templates/style.css notes/

python mdkindle.py

for file in notes/*.md ; do
	new=${file%.md}.html
	cat templates/header.html > $new
	markdown $file >> $new
	cat templates/footer.html >> $new
	rm $file
done
