#!/usr/bin/env bash
# reload service ©2024, Ovais Quraishi

SRVC_CONFIG_FILE=srvc_run_config.env

# Load .env file if present
if [[ -f ./${SRVC_CONFIG_FILE} ]]; then
    source ./${SRVC_CONFIG_FILE}
else
    echo "Unable to find config.env. Expecting ENV vars to be set externally" >&2
fi

systemctl status ${SRVC_NAME} |  sed -n 's/.*Main PID: \(.*\)$/\1/g p' | cut -f1 -d' ' | xargs kill -HUP
