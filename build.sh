#!/usr/bin/env bash

# Function to create a directory if it doesn't exist
create_directory() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        echo "Creating directory: ${dir}"
        mkdir -p "${dir}"
    else
        echo "Directory ${dir} already exists."
    fi
}

# Function to increment the patch version in a semver string
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

# Environment variables file
SRVC_CONFIG_FILE="srvc_run_config.env"

# Load .env file if present
if [[ -f "$SRVC_CONFIG_FILE" ]]; then
    source "$SRVC_CONFIG_FILE"
else
    echo "Unable to find $SRVC_CONFIG_FILE. Expecting ENV vars to be set externally" >&2
    exit -1
fi

# Increment patch version
new_ver=$(inc_patch "ver.txt")
be_build_dir="builds/BE_${new_ver}"
create_directory "${be_build_dir}"

# Copy necessary files to the build directory
files_to_copy=("docker_install_srvc.sh" "install_srvc.sh" "Dockerfile" "setup.config.template" "ver.txt" "build_docker.py")
for file in "${files_to_copy[@]}"; do
    cp "$file" "${be_build_dir}"
done

# Build package name
build_pkg_name="${SRVC_NAME}-${new_ver}.tar.gz"
echo "Building $build_pkg_name"
tar -czf "${build_pkg_name}" $(<file_manifest.txt)
echo "Compressing $build_pkg_name"

if [[ -f "${build_pkg_name}" ]]; then
    echo "${build_pkg_name} Done"
    mv "${build_pkg_name}" "${be_build_dir}"
else
    echo "${build_pkg_name} failed"
fi

# Calculate SHA256 hash of the package
pkg_sha256=$(sha256sum "${be_build_dir}/${build_pkg_name}" | awk '{print $1}')

# Create build information file
build_info_file="BUILD_INFO.TXT"
{
    echo "SERVICE=${SRVC_NAME}"
    echo "VERSION=${new_ver}"
    echo "PACKAGE=${build_pkg_name}"
    echo "PKGSHA256=${pkg_sha256}"
    echo "SRVC_DIR=/usr/local/rollama/"
} > "${build_info_file}"

mv "$build_info_file" "${be_build_dir}"

echo "Build Info"
tree "${be_build_dir}"
cd "${be_build_dir}"
cat "$build_info_file"
