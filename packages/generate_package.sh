#!/bin/sh

# Bruno Adele < bruno.adele@jesuislibre.org >
VERSION=0.1
TMP=/tmp
PACKAGE=$TMP/package
PWD=`pwd`

if [ -d "$PACKAGE" ]; then
  rm -rf $PACKAGE
fi

if [ -e "$PACKAGE" ]; then
  rm $TMP/jsl-tools.tgz
fi


mkdir -p $PACKAGE
cp ../fdedup/jsl-fdedup.py "$PACKAGE/"

cd "$PACKAGE/"
tar  -cvzf $TMP/jsl-tools-$VERSION.tgz  .
cd "$PWD"
