virtualenv --python=/usr/bin/python3.6 v-env
source v-env/bin/activate
pip install -r ../requirements.txt
deactivate
cd v-env/lib/python3.6/site-packages/
zip -r9 ../../../../slamonitor-lambda-code.zip .
cd ../../../../
zip -g -j slamonitor-lambda-code.zip ../src/*

