#!/bin/bash
# clean:
rm -rf tmp_*

doconce2format LaTeX easyviz.do.txt
mv easyviz.ctex tmp_easyviz.ctex
ctex2tex -code2verb 1 tmp_easyviz
latex tmp_easyviz
latex tmp_easyviz
dvips -o tmp_easyviz.ps tmp_easyviz.dvi
ps2pdf tmp_easyviz.ps
