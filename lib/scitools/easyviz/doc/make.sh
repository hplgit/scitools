#!/bin/bash -x
# clean:
rm -rf tmp_*

cp easyviz.do.txt tmp_easyviz.do.txt

doconce2format HTML tmp_easyviz.do.txt

doconce2format LaTeX tmp_easyviz.do.txt
ptex2tex tmp_easyviz
latex tmp_easyviz
latex tmp_easyviz
dvips -o tmp_easyviz.ps tmp_easyviz.dvi
ps2pdf tmp_easyviz.ps

doconce2format wiki tmp_easyviz.do.txt



