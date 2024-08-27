#!/bin/sh

git diff --no-index $@ | sed 's/before\///g' | sed 's/after_reference\///g'