#!/bin/bash
## sole parameter is an integer indicating incremental daily version
BUILD_TAG=dbcawa/feewaiver:v$(date +%Y.%m.%d).$1
git checkout dbca_dev &&
git pull &&
cd feewaiver/frontend/feewaiver/ &&
npm run build &&
cd ../../../ &&
source venv/bin/activate &&
./manage_fw.py collectstatic --no-input &&
git log --pretty=medium -30 > ./fw_git_history &&
docker image build --no-cache --tag $BUILD_TAG . &&
git checkout working &&
echo $BUILD_TAG &&
docker push $BUILD_TAG
