#!/bin/sh

# python -m cProfile -o /tmp/result script.py 
pyprof2calltree -i /tmp/result -k
