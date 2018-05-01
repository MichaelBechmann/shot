#! /bin/bash
# copy generated files from the foundation sub-project to the web2py directories

echo 'Copy files created by the Foundation stack into the web2py environment ...'

dest=../static

src=../foundation_prj/dist/assets/css
rsync -r $src $dest -v

src=../foundation_prj/dist/assets/js
rsync -r $src $dest -v

echo 'done.'