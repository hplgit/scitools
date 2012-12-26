#!/bin/sh
scitools pyreport -l -e -t pdf  -o report_mpl -a '0.05 9' demo_pyreport.py
scitools pyreport -l -e -t html -o report_mpl -a '0.05 9' demo_pyreport.py
scitools pyreport -l -e -t pdf  -o report_evz -a '0.05 9 easyviz' demo_pyreport.py
scitools pyreport -l -e -t html -o report_evz -a '0.05 9 easyviz' demo_pyreport.py
