#!/usr/bin/env python3
import sys

with open(sys.argv[1]) as pemfile:
    p = pemfile.read()
    print(p.replace('\n', '\\n'))