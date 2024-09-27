#!/usr/bin/env bash

tag_ver=$(cat ver.txt)
echo "git tag -a ${tag_ver} -m \"v${tag_ver}\""
git tag -a ${tag_ver} -m \"v${tag_ver}\"
echo "git push origin ${tag_ver}"
git push origin ${tag_ver}
