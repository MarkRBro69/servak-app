#!/bin/bash

if kind get clusters | grep -q "kind"; then
    echo "Cluster exists, start loading"

    kind load docker-image servak-users_service:latest
    kind load docker-image servak-user_interface_service:latest
    kind load docker-image servak-posts_service:latest
    kind load docker-image servak-nginx:latest

    echo "Images loaded"
else
    echo "Cluster does not exists"
fi