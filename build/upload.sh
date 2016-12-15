#!/bin/bash
cd ___output/linux-32
find . -type f -exec anaconda upload {} \;
cd ../linux-64
find . -type f -exec anaconda upload {} \;

