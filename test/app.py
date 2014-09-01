from celery import Celery

app = Celery(
        broker='amqp://admin:2hXK9cMLw4Bu@127.0.0.1:5672'
        )

@app.task()
def add(x, y):
    return x + y

if __name__ == '__main__':
    from pprint import pprint
    app.worker_main(argv=['worker', '--pidfile=test.pid', '-D'])
