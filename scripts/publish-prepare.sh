# !/bin/bash
set -e

# local pypirc for staging file ~/.pypirc.test
# local pypirc for release file ~/.pypirc.release
# local pypirc destination file ~/.pypirc

if [ "$1" = "staging" ]; then
    cp ~/.pypirc.test ~/.pypirc
else
    cp ~/.pypirc.release ~/.pypirc
fi


