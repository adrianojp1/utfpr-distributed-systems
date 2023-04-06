# Project 1 - Farm Event Driven Simulator

A simple farm simulation based on event driven architecture.

It uses RabbitMQ messaging with python pika AMQP implementation library. 
Based on https://www.rabbitmq.com/tutorials/tutorial-one-python.html

## Simulation description
The application simulates the management of a farm with two message producer clients, represented as sensors at the truck yard gate and in the beans silo, and three subscribers, fleet management, grain stock control and the farmer's app. The gate sensor sends messages to the exchange, or topic, "trucks" of incoming and outgoing trucks with their respective loads in percentage, while the silo sensor sends messages to the topic "beans" with the silo load in percentage. On the subscriber side, grain stock receives messages from "beans" and stores the currently available bean load, fleet management receives "trucks" and stores which trucks are on and off the farm. Finally, the farmer's app receives from both topics, notifies the user whenever a truck passes through the gate and suggests that the farmer reload the silo if its load is less than 30% of capacity.

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
