# Project 4 - Order Shipping Choreography Saga

A simple kotlin application simulating an order shipping service based 
on event driven **choreography saga** architecture with RabbitMQ.

## Description
The simulation is implemented in two parts. A service that receive orders, generates
shipping requests and consumes shipping events to update the orders.
While the other one is able to receive updates on the count of products in stock,
consume shipping requests events and generate shipping events accordingly
with the availability of the requested product.

## Descrição (pt-br)
A simulação é implementada em duas partes. Um serviço que recebe pedidos, gera
requisições de remessas e consome eventos de remessas para atualizar os pedidos. 
Enquanto o outro é capaz de receber atualizações da quantidade de produtos em estoque,
consumir eventos de requisições de remessas e gerar eventos de remessas de acordo
com a disponibilidade do produto requisitado.
