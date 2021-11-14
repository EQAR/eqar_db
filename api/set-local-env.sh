#!/bin/bash
#
# set environment based on .env file for Django not running in Docker
#

set -a

# has DJANGO_SECRET_KEY & DJANGO_DB_PASS
source ../.env

DJANGO_DB_HOST=127.0.0.1
DJANGO_DB_NAME=eqar
DJANGO_DB_USER=eqar

set +a

