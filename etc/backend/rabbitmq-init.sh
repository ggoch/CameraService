#!/bin/bash

# 设置 RabbitMQ 节点名
NODE=rabbit@$(hostname)

# 等待 RabbitMQ 服务器启动
until rabbitmqctl -n $NODE status; do
  sleep 5;
done;

# 创建新用户并设置权限
rabbitmqctl -n $NODE add_user celery celery
rabbitmqctl -n $NODE set_user_tags celery administrator
rabbitmqctl -n $NODE set_permissions -p / celery ".*" ".*" ".*"