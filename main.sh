source ./env/bin/activate

uvicorn api.views:app --reload

deactivate