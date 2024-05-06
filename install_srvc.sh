#!/usr/bin/env bash

# create directory if it doesn't exist
create_directory() {
    local DIR=$1
    if [ ! -d "$DIR" ]; then
        echo "Creating directory: ${DIR}"
        mkdir -p "${DIR}"
    else
        echo "Directory ${DIR} already exists."
    fi
}

# check and create group if it doesn't exist
check_and_create_group() {
    local GROUP=$1
    if ! grep -q "^${GROUP}:" /etc/group; then
        echo "Creating group: ${GROUP}"
        addgroup "${GROUP}"
    else
        echo "Group ${GROUP} already exists."
    fi
}

# check and create user if it doesn't exist
check_and_create_user() {
    local USER=$1
    local GROUP=$2
    if ! id -u "$USER" > /dev/null 2>&1; then
        echo "Creating user: ${USER}"
        adduser --system --no-create-home --ingroup "${GROUP}" "${USER}"
    else
        echo "User ${USER} already exists."
    fi
}

# load config file
load_config_file() {
    local CONFIG_FILE=$1
    if [[ -f ${CONFIG_FILE} ]]; then
        source ${CONFIG_FILE}
    else
        echo "Unable to find ${CONFIG_FILE}. Expecting ENV vars to be set externally" >&2
        exit -1
    fi
}

# load build info
BUILD_INFO=BUILD_INFO.TXT
load_config_file "${BUILD_INFO}"

echo "Install Pkg"
# user and group name is same as service name
GROUP=${SERVICE}
USER=${SERVICE}

check_and_create_group "${GROUP}"
check_and_create_user "${USER}" "${GROUP}"
create_directory "${SRVC_DIR}"

echo "tar xfz ./${PACKAGE} -C ${SRVC_DIR} 2> /dev/null"
tar xfz ./${PACKAGE} -C ${SRVC_DIR} 2> /dev/null

# load service config file
SRVC_CONFIG_FILE=${SRVC_DIR}/srvc_run_config.env
load_config_file "${SRVC_CONFIG_FILE}"

echo "Setting up Service"
pip3 install -r ${SRVC_DIR}/requirements.txt --quiet
create_directory "${SRVC_CONFIG_DIR}"
mv ${SRVC_DIR}/setup.config.template ${SRVC_CONFIG_DIR}/setup.config
mv ${SRVC_DIR}/rollama.service ${SYSD_DIR}
systemctl enable rollama.service
