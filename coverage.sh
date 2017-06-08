#!/bin/bash

unset http_proxy
unset https_proxy
coverage run stampy.py
coveralls
