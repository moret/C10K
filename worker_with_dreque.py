from dreque import DrequeWorker
from redis import StrictRedis


def long_crypt_job(rand, uid):
    print 'request uid: %d' % uid
    result = 1
    for i in range(1, rand):
        result *= i
    print 'job done: %d! = %s\n' % (rand, result)
    StrictRedis().set(uid, result)

worker = DrequeWorker(['queue'], 'localhost')
worker.work()
