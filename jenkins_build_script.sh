#!/bin/bash

# Build package, then build docker image, push the docker image
#  to private image registry running accessible on a local
#  network only
#
# IMPORTANT: Assumes that the node where this script will be run has
#   "kubectl" installed and has deployment access to the destination
#   kubernetes cluster
#
# Assumes that image reposity url is:
#   docker-registry:5000

check_namespace() {
  name_space="$1"
  # Run the command and capture its output
  output=$(kubectl get namespace | grep ${name_space} | awk '{print $1}')

  # Check if the output is empty (i.e., only one line)
  if [ -n "$output" ]; then
    echo "**** Namespace [${name_space}] already exists"
    return 0
  else
    echo "**** Namespace [${name_space}] does not exist"
    return 1
  fi
}

check_pod_status() {
  namespace_name="$1"
  iterations=0
  while [ $iterations -lt 10 ]; do
    output=$(kubectl -n "${namespace_name}" get pods | grep rollama | head -n1)
    if [ "$output" == "Running" ]
    then
      echo "Pod is running."
      return
    elif [ $iterations -ge 10 ]; then
      echo "Failed to start pod after 10 attempts"
      exit 1 # hard exit with a non-zero status code
    else
      echo "**** Output not yet 'Running', trying again..."
      sleep 2
      ((iterations++))
    fi
  done
}

compare_strings() {
  local recent_git_tag_commit_id="$1"
  local recent_commit_id="$2"
  local recent_git_tag="$3"

  if [ "${recent_git_tag_commit_id}" = "${recent_commit_id}" ]
  then
    echo "Both Git Tag and Git Commit ID match"
    export srvc_ver=$recent_git_tag
  else
    echo "Strings are not equal"
  fi
}

echo "**** Setting Git user name and email"
git config --global user.name "Jenkins Build"
git config --global user.email "no-reply@ifthenelse.org"

export curr_git_tag=$(git describe --abbrev=0)
export curr_git_tag_commit_id=$(git rev-list -n 1 $curr_git_tag)
export curr_commit_id=$(git rev-parse HEAD)

compare_strings "${curr_git_tag_commit_id}" "${curr_commit_id}" "${curr_git_tag}"

echo "**** Building Package"
./build.sh > /dev/null 2>&1

# build script increments the build number
export srvc_ver=$(<ver.txt)

echo "**** v${srvc_ver} successfully built"
cd builds/BE_${srvc_ver}

echo "**** Configuring Build v${srvc_ver}"
scp ovais@localhost:/home/ovais/rollama/setup.config .

echo "**** Creating Docker image rollama:${srvc_ver}"
./build_docker.py > /dev/null 2>&1

echo "**** Clean up config"
rm -f setup.config

echo "**** Pushing Docker Image rollama:${srvc_ver} to remote registry"
docker tag rollama:${srvc_ver} docker:5000/rollama:${srvc_ver} > /dev/null 2>&1
docker tag rollama:latest docker:5000/rollama:latest > /dev/null 2>&1
docker push docker:5000/rollama:${srvc_ver} > /dev/null 2>&1
docker push docker:5000/rollama:latest > /dev/null 2>&1

echo "**** Cleaning up orphaned images"
# List orphaned images (those with the <none> tag)
orphaned_images=$(docker image ls --filter "dangling=true" -q)

# Check if there are any orphaned images
if [ -n "$orphaned_images" ]
then
    echo "**** Removing orphaned docker images"
    # Remove orphaned images
    docker image rm $orphaned_images > /dev/null 2>&1
    echo "**** Cleaning up local docker images"
    # Remove specific local images
    docker image rm rollama:${srvc_ver} > /dev/null 2>&1
    docker image rm rollama:latest > /dev/null 2>&1
else
    echo "**** No orphaned docker images found"
    echo "**** Cleaning up local docker images"
    # Remove specific local images
    docker image rm rollama:${srvc_ver} > /dev/null 2>&1
    docker image rm rollama:latest > /dev/null 2>&1
fi

# check if namespace exists
srvc_name_tag=$(echo "$srvc_ver" | sed 's/^\([0-9]*\)\.\([0-9]*\)\.\([0-9]*\)$/v\1-\2-\3/')
namespace="ollamagpt-${srvc_name_tag}"

if ! check_namespace "${namespace}"
then
    echo "**** Creating namespace: ${namespace}"
    kubectl create namespace "${name_space}"
    echo "**** Deploying Rollama v${srvc_ver} to namespace [${name_space}]"
    echo "**** Deployment"
    # deployment defaults to "latest" tag
    kubectl -n "${namespace}" apply -f deployment.yaml
    echo "**** Service v${srvc_ver}"
	  echo "${PWD}"
	  sed -i '' 's|SEMVER|"${srvc_ver}"|' service.yaml
    kubectl -n "${namespace}" apply -f service.yaml
    check_pod_status "${namespace}"
    echo "**** Pod is now Running"
    kubectl -n "${namespace}" get pods
		git checkout service.yaml
else
    echo "**** Not Creating Namespace"
    echo "**** Deploying Rollama v${srvc_ver} to namespace [${name_space}]"
    echo "**** Deployment"
    kubectl -n "${namespace}" apply -f deployment.yaml
    echo "**** Service v${srvc_ver}"
    sed -i '' 's|SEMVER|"${srvc_ver}"|' service.yaml
    kubectl -n "${namespace}" apply -f service.yaml
		check_pod_status "${namespace}"
		echo "**** Pod is now Running in namespace: ${namespace}"
		kubectl -n "${namespace}" get pods
fi

# change directory back to source root
cd -

echo "**** Get Healthcheck of the service"
k8_srvc_name=$(kubectl -n "${namespace}" get svc -o name | sed -e 's/service\///g')
k8_srvc_nodeport=$(kubectl -n "${namespace}" get svc "${k8_srvc_name}" -o jsonpath='{.spec.ports[0].nodePort}')
running_srvc_ver=$(curl -X GET -s "http://k8prod-1.ifthenelse.org:${k8_srvc_nodeport}/version")
if [ -n "${running_srvc_ver}" ]
then
	  echo "**** Running service version: ${running_srvc_ver}"
    if [ "${curr_git_tag_commit_id}" != "${curr_commit_id}" ]
    then
        export new_tag=$(<ver.txt)
    	  echo "**** Applying and pushing New Tag ${new_tag}"
    	  ./git_tag_push.sh
        echo "**** Pushing new ver.txt to remote repo"
        git add ver.txt
        git commit -m "Updating version to ${new_tag}"
        git push origin HEAD:main
    fi
    exit 0
else
	  echo "ERROR:**** Service is not running"
    exit -1
fi
