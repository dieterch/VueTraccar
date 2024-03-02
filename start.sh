# fresh compile at startup
python prepare.py
pushd ./frontend
npm install
npm run justbuild
popd
export PRODUCTION="1" 
python -OO app.py
