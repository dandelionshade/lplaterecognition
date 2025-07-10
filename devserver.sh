#!/bin/sh
python -u -m flask --app main run -p ${PORT:-8000} --debug
