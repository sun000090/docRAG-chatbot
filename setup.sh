rm -rf ./env

python3.10 -m venv env

source ./env/bin/activate

pip install -q -r requirements.txt

python3 --version

deactivate