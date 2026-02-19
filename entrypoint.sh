#!/bin/bash
# Ensure errors.log is a file, not a directory
if [ -d errors.log ]; then
    rm -rf errors.log
fi
if [ ! -f errors.log ]; then
    touch errors.log
fi

# Start the weather service
exec python weather_service.py
