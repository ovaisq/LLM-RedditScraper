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

# increment the patch version in a semver string
inc_patch() {
    local ver_file=$1
    local ver_string
    local ver_parts

    # read semantic versioning string from the file
    read -r ver_string < "$ver_file"

    # split on '.' into an array
    IFS='.' read -r -a ver_parts <<< "$ver_string"

    # increment the patch level by one
    ((ver_parts[2]++))

    # backup original version in a file named 'previous_ver.txt'
    echo "$ver_string" > previous_ver.txt

    # reconstruct the version string and update the file with the new semver string
    ver_string="${ver_parts[0]}.${ver_parts[1]}.${ver_parts[2]}"
    echo "$ver_string" > "$ver_file"

    echo "$ver_string"
}

# environment variables file
SRVC_CONFIG_FILE="srvc_run_config.env"

# load .env file if present
if [[ -f "$SRVC_CONFIG_FILE" ]]; then
    source "$SRVC_CONFIG_FILE"
else
    echo "Unable to find $SRVC_CONFIG_FILE. Expecting ENV vars to be set externally" >&2
    exit -1
fi

# increment patch version
NEW_VER=$(inc_patch "ver.txt")

create_directory "builds/${NEW_VER}"

cp docker_install_srvc.sh "builds/${NEW_VER}"
cp install_srvc.sh "builds/${NEW_VER}"
cp Dockerfile "builds/${NEW_VER}"
cp setup.config.template "builds/${NEW_VER}"
cp ver.txt "builds/${NEW_VER}"
cp build_docker.py "builds/${NEW_VER}"

BUILD_PKG_NAME="${SRVC_NAME}-${NEW_VER}.tar"
echo "Building $BUILD_PKG_NAME"
tar -cf "${BUILD_PKG_NAME}" $(<file_manifest.txt)
echo "Compressing $BUILD_PKG_NAME"
gzip "$BUILD_PKG_NAME"

if [[ -f "${BUILD_PKG_NAME}.gz" ]]; then
    echo "${BUILD_PKG_NAME}.gz Done"
    PKG_NAME="${BUILD_PKG_NAME}.gz"
	mv ${PKG_NAME} "builds/${NEW_VER}"
else
    echo "${BUILD_PKG_NAME}.gz failed"
fi

BUILD_INFO_FILE="BUILD_INFO.TXT"

PKGSHA256=$(sha256sum "builds/${NEW_VER}/$PKG_NAME" | awk '{print $1}')

# Create build information file
{
    echo "SERVICE=${SRVC_NAME}"
    echo "VERSION=${NEW_VER}"
    echo "PACKAGE=${PKG_NAME}"
    echo "PKGSHA256=${PKGSHA256}"
    echo "SRVC_DIR=/usr/local/rollama/"
} > "$BUILD_INFO_FILE"

mv $BUILD_INFO_FILE "builds/${NEW_VER}"

echo "Build Info"
tree "builds/${NEW_VER}"
cd "builds/${NEW_VER}"
cat "$BUILD_INFO_FILE"
