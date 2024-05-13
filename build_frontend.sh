#!/usr/bin/env bash
# tarball frontend

# Function to create directory if it doesn't exist
create_directory() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        echo "Creating directory: $dir"
        mkdir -p "$dir"
    else
        echo "Directory $dir already exists."
    fi
}

# Function to increment patch version
inc_patch() {
    local ver_file=$1
    local ver_string
    local ver_parts

    # Read semantic versioning string from the file
    read -r ver_string < "$ver_file"

    # Split on '.' into an array
    IFS='.' read -r -a ver_parts <<< "$ver_string"

    # Increment the patch level by one
    ((ver_parts[2]++))

    # Backup original version in a file named 'previous_ver.txt'
    echo "$ver_string" > previous_ver.txt

    # Reconstruct the version string and update the file with the new semver string
    ver_string="${ver_parts[0]}.${ver_parts[1]}.${ver_parts[2]}"
    echo "$ver_string" > "$ver_file"

    echo "$ver_string"
}

# Main script starts here

SRVC_NAME="rollama-FE"
TOP_LEVEL_DIR="frontend/analysis_frontend"
BUILD_DIR="builds/FE_$(inc_patch "${TOP_LEVEL_DIR}/ver.txt")"
NEW_VER=$(cat "${TOP_LEVEL_DIR}/ver.txt")
BUILD_PKG_NAME="${SRVC_NAME}-${NEW_VER}.tar.gz"

# Create build directory if it doesn't exist
create_directory "$BUILD_DIR"

# Copy necessary files to build directory
cp -f fe_docker_install_srvc.sh FE_Dockerfile fe_build_docker.py "${TOP_LEVEL_DIR}/ver.txt" "$BUILD_DIR"

# Build the package
echo "Building $BUILD_PKG_NAME"
tar -czf "$BUILD_PKG_NAME" \
    --exclude=__pycache__ \
    --exclude=db.sqlite3 \
    --exclude='media*' \
    --exclude='.log' \
    --exclude='.pot' \
    --exclude='.pyc' \
    --exclude=setup.config \
    -C "${TOP_LEVEL_DIR}/.." analysis_frontend

# Move the package to the build directory if created successfully
if [[ -f "$BUILD_PKG_NAME" ]]; then
    echo "$BUILD_PKG_NAME Done"
    mv "$BUILD_PKG_NAME" "$BUILD_DIR/"
else
    echo "$BUILD_PKG_NAME failed"
fi

# Create build information file
BUILD_INFO_FILE="FE_BUILD_INFO.TXT"
PKGSHA256=$(sha256sum "$BUILD_DIR/$BUILD_PKG_NAME" | awk '{print $1}')
{
    echo "SERVICE=$SRVC_NAME"
    echo "VERSION=$NEW_VER"
    echo "PACKAGE=$BUILD_PKG_NAME"
    echo "PKGSHA256=$PKGSHA256"
    echo "SRVC_DIR=/usr/local/"
} > "$BUILD_INFO_FILE"

# Move build information file to build directory
mv "$BUILD_INFO_FILE" "$BUILD_DIR"

# Display build info
echo "Build Info"
tree "$BUILD_DIR"
cat "$BUILD_DIR/$BUILD_INFO_FILE"

