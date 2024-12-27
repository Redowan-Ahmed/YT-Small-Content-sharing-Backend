#!/bin/sh

# Start RabbitMQ in the background
rabbitmq-server &
rabbitmq_pid=$!

# Wait for RabbitMQ to start
sleep 10

# Create virtual hosts
rabbitmqctl add_vhost video

# Create users and set permissions
rabbitmqctl add_user redowan password
rabbitmqctl set_permissions -p video redowan ".*" ".*" ".*"

# Stop RabbitMQ background process
kill $rabbitmq_pid

# Restart RabbitMQ in the foreground
exec rabbitmq-server
