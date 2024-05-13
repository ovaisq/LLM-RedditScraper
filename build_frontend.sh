#!/usr/bin/env bash
# tarball frontend

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

SRVC_NAME="rollama-frontend"
TOP_LEVEL_DIR="analysis_frontend"
cd "${TOP_LEVEL_DIR}"
# increment patch version
NEW_VER=$(inc_patch "ver.txt")
cd -
BUILD_DIR="builds/FE_${NEW_VER}"
BUILD_PKG_NAME="${SRVC_NAME}-${NEW_VER}.tar.gz"

create_directory "${BUILD_DIR}"

cp fe_docker_install_srvc.sh "${BUILD_DIR}"
cp FE_Dockerfile "${BUILD_DIR}"
cp "${TOP_LEVEL_DIR}"/ver.txt "${BUILD_DIR}"

cp fe_build_docker.py "${BUILD_DIR}"

echo "Building $BUILD_PKG_NAME"
tar -czf ${BUILD_PKG_NAME} \
	--exclude=__pycache__ \
	--exclude=db.sqlite3 \
	--exclude='media*' \
	--exclude='.log' \
	--exclude='.pot' \
	--exclude='.pyc' \
	--exclude=setup.config \
	"${TOP_LEVEL_DIR}"

if [[ -f "${BUILD_PKG_NAME}" ]]; then
    echo "${BUILD_PKG_NAME} Done"
    PKG_NAME="${BUILD_PKG_NAME}"
    mv ${PKG_NAME} "${BUILD_DIR}"
else
    echo "${BUILD_PKG_NAME} failed"
fi

BUILD_INFO_FILE="FE_BUILD_INFO.TXT"

PKGSHA256=$(sha256sum "${BUILD_DIR}/$PKG_NAME" | awk '{print $1}')

# Create build information file
{
    echo "SERVICE=${SRVC_NAME}"
    echo "VERSION=${NEW_VER}"
    echo "PACKAGE=${PKG_NAME}"
    echo "PKGSHA256=${PKGSHA256}"
    echo "SRVC_DIR=/usr/local/"
} > "$BUILD_INFO_FILE"

mv $BUILD_INFO_FILE "${BUILD_DIR}" 

echo "Build Info"
tree "${BUILD_DIR}"
cd "${BUILD_DIR}"
cat "$BUILD_INFO_FILE"
