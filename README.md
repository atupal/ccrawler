ccrawler
========
A distributed crawler use [celery](celeryproject.org)+[gevent](http://gevent.org/)+[redis](http://redis.io/)

archtecture
===========
![Image](../master/artwork/ccrawler-arch.png?raw=true)

configuration
=============
couchdb:
> CouchDB won’t recover from this error on its own. To fix it, you need to edit /usr/bin/couchdb(it’s a Bash script). At the beginning of the script, there’s a variable named RESPAWN_TIMEOUT. It’s set to 0 by default, simply change it to say 5 and restart CouchDB. That should fix it.
