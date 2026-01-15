#!/bin/env bash

VENV_DIR="./venv"

if [ -d $VENV_DIR ]; then
	source $VENV_DIR/bin/activate
else
	echo "venv doesn't exist, creating one..."
	python -m venv venv
	source $VENV_DIR/bin/activate
	pip install -r requirements.txt
fi

uvicorn store.main:app --reload
