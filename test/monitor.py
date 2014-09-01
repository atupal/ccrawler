
from celery import Celery

def my_monitor(app):
    state = app.events.State()

    def announce_failed_tasks(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])

        print('TASK FAILED: %s[%s] %s' % (task.name, task.uuid, task.info(),))

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
            'task-failed': announce_failed_tasks,
            })
        recv.capture(limit=None, timeout=None, wakeup=True)

if __name__ == '__main__':
    from app import app
    my_monitor(app)
