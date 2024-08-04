#!/bin/sh

flask db upgrade

exec gunicorn --binf 0.0.0.0:80 "app:create_app()"
