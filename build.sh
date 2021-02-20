#!/bin/bash
set -x

### Used as part of a jenkins build.
### Need to have WORKSPACE  /  BUILD_ID  /  BUILD_NUMBER and  defined

export MAJOR=1
export MINOR=0
export PATCH=0
export PATH=/usr/bin:/home/jenkins_01:$PATH
export VERSION=${MAJOR}.${MINOR}.${PATCH}.${BUILD_NUMBER}
export SHORT_VERSION=${MAJOR}.${MINOR}.${PATCH}

export zip="/home/jenkins_01/zip"

cd ${WORKSPACE}
zip_file="whole_unit_test_v${VERSION}.zip"
version_file="whole_unit_test/version.txt"
echo "${VERSION}" > ${version_file}
${zip} -r ${zip_file} whole_unit_test
