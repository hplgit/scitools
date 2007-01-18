#!/bin/bash -x
# clean:
rm -rf tmp_*

# HTML:
# first covert to PNG format:
cd figs
for i in *.eps; do echo "convert $i"; if [ ! -f $i.png ]; then convert $i png:$i.png; fi; done
cd ..
cp easyviz.do.txt tmp_easyviz.do.txt
doconce2format HTML tmp_easyviz.do.txt
subst.py '\.eps"' '.eps.png"' tmp_easyviz.html

exit

doconce2format LaTeX easyviz.do.txt
mv easyviz.ctex tmp_easyviz.ctex
ctex2tex -code2verb 1 tmp_easyviz
latex tmp_easyviz
latex tmp_easyviz
dvips -o tmp_easyviz.ps tmp_easyviz.dvi
ps2pdf tmp_easyviz.ps

