#!/bin/bash

# Build package, then build docker image, push the docker image
#  to private image registry running accessible on a local 
#  network only
#
# IMPORTANT: Assumes that the node where this script will be run has
#	"kubectl" installed and has deployment access to the destination
#	kubernetes cluster
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
	while true 
    do
    	output=$(kubectl -n "${namespace_name}" get pods | grep rollama | head -n1 | awk '{print $3}')
  
  		if [ "$output" == "Running" ]
        then
    		break
  		else
    		echo "**** Output not yet 'Running', trying again..."
    		sleep 2
  		fi
	done
}

echo "**** Building Package"
./build.sh > /dev/null 2>&1

export srvc_ver=$(<ver.txt)
cd builds/BE_${srvc_ver}

echo "**** Configuring Build"
# change this to suit your needs
scp localhost:/apps/rollama/setup.config .

echo "**** Creating Docker image"
./build_docker.py > /dev/null 2>&1

echo "**** Clean up config"
rm -f setup.config

echo "**** Pushing Docker Image to Registry"
docker tag rollama:${srvc_ver} dockeri-registry:5000/rollama:${srvc_ver} > /dev/null 2>&1
docker push docker-registry:5000/rollama:${srvc_ver} > /dev/null 2>&1

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
        echo "**** Creating namespace"
        kubectl create namespace "${name_space}"
        echo "**** Deploying Rollama v${srvc_ver} to namespace [${name_space}]"
        echo "**** Deployment"
        kubectl -n "${namespace}" apply -f deployment.yaml
        echo "**** Service"
        kubectl -n "${namespace}" apply -f service.yaml
		check_pod_status "${namespace}"
		echo "**** Pod is now Running"
        kubectl -n "${namespace}" get pods
else
        echo "**** Not Creating Namespace"
        echo "**** Deploying Rollama v${srvc_ver} to namespace [${name_space}]"
        echo "**** Deployment"
        kubectl -n "${namespace}" apply -f deployment.yaml
        echo "**** Service"
        kubectl -n "${namespace}" apply -f service.yaml
		check_pod_status "${namespace}"
		echo "**** Pod is now Running"
		kubectl -n "${namespace}" get pods
fi

echo "**** Get Healthcheck of the service"
k8_srvc_name=$(kubectl -n "${namespace}" get svc -o name | sed -e 's/service\///g')
k8_srvc_nodeport=$(kubectl -n "${namespace}" get svc "${k8_srvc_name}" -o jsonpath='{.spec.ports[0].nodePort}')
running_srvc_ver=$(curl -X GET -s "http://k8prod-1.ifthenelse.org:${k8_srvc_nodeport}/version")
if [ -n "${running_srvc_ver}" ]
then
	echo "**** Running service version: ${running_srvc_ver}"
    exit 0
else
	echo "**** Service is not running"
    exit -1
fi
