#!/bin/sh

./clean.sh

./pack.sh

sftp lanpi <<'EOF'
	rm websites/comp10120-w6-tut/server/*
	rm websites/comp10120-w6-tut/static/*
	put -fR publish/server websites/comp10120-w6-tut
	put -fR publish/static websites/comp10120-w6-tut
EOF
