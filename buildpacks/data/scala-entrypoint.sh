#!/bin/sh

if [ "$#" -gt 0 ]; then
  exec "$@"
else
  exec java $ENTRYPOINT_ARGS -jar app.jar
fi
