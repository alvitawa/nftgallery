#!/bin/bash

rm -rf art.github.io/*
cp dev/* art.github.io/

cd art.github.io

git checkout "CNAME" #Cancel deletion
git add *
git commit -m "Automated commit."
git push

cd ..