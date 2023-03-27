# Work 1

RabbitMQ messaging with python pika library. Based on https://www.rabbitmq.com/tutorials/tutorial-one-python.html

---

## Running

If the docker boot fails with this error:
```
failed to open log file at '/var/log/rabbitmq/rabbit@58e454128146_upgrade.log', reason: permission denied
```

Execute the following command to allow all users to write to RabbitMQ log:
```
sudo chmod -R 777 .docker/rabbitmq/log
```
