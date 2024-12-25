#!/usr/bin/env bash

# Build the docker image

module_path=$1
target_dir_name=$2
dockerfile_path=$3
tag=$4
image=$5

docker buildx build --platform linux/amd64 \
-t "${image}:${tag}" \
-f ${dockerfile_path} . \
--build-arg module_path=${module_path} \
--build-arg target_dir_name=${target_dir_name} \
--output type=docker
