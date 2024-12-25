#!/bin/bash

services=("user_interface_service" "users_service" "posts_service" "chats_service")

for service in "${services[@]}"; do
    cd "$service" || exit

    pip freeze > requirements.txt

    cd ..
done