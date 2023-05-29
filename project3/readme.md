Aplicativo de Leilão utilizando Flask SSE

To run the server:
```
gunicorn app:app --worker-class gevent --bind 127.0.0.1:8000
```