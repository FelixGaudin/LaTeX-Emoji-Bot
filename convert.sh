#!/bin/sh

# Super tex maker
pdflatex $1.tex 1> /dev/null 2> /dev/null

# Touche pas à ça petit con
convert -border 80 -density 500 -quality 300 -trim +repage -border 40 -bordercolor transparent $1.pdf $1.png

# ¯\_(ツ)_/¯
height=`convert $1.png -format "%h" info:`
width=`convert $1.png -format "%[fx:w]" info:`
minwidth=1000
newwidth=$(( width > minwidth ? width : minwidth ))
convert -background transparent -extent ${newwidth}x${height} $1.png $1.png

# Remove dependancies
rm $1.pdf $1.log $1.aux $1.tex
rm -r $1 2> /dev/null