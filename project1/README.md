# Project 1 - Farm Event Driven Simulator

A simple farm simulation based on event driven architecture.

It uses RabbitMQ messaging with python pika AMQP implementation library. 
Based on https://www.rabbitmq.com/tutorials/tutorial-one-python.html

---

## Running

1. Install required python libs with `requirements.txt` (virtual env recommended)
2. Run `docker-compose.yml`
2. Run all python files on `./src` directory in separated terminals

---

If the docker boot fails with this error:
```
failed to open log file at '/var/log/rabbitmq/rabbit@58e454128146_upgrade.log', reason: permission denied
```

Execute the following command to allow all users to write to RabbitMQ log:
```
sudo chmod -R 777 .docker/rabbitmq/log
```
