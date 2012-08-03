import json
import random
import datetime
import tornado.ioloop
import tornado.web
import tornado.httpclient
from tornado.web import asynchronous
from dreque import Dreque
from redis import StrictRedis

two_secs = datetime.timedelta(seconds=2)
func_name = 'worker_with_dreque.long_crypt_job'


def reset_queue():
    Dreque('localhost').remove_queue('queue')
    Dreque('localhost').watch_queue('queue')


def asynch_check_job(function, uid):
    def cb():
        function(uid)
    tornado.ioloop.IOLoop.instance().add_timeout(two_secs, cb)


class MainHandler(tornado.web.RequestHandler):
    @asynchronous
    def get(self):
        rand = random.randint(20, 30)

        self.write('calculating %d!\n' % rand)
        self.flush()

        enqueue_url = 'http://localhost:8888/enqueue/%d' % rand
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(enqueue_url, self.handle_enqueue)

    @asynchronous
    def handle_enqueue(self, response):
        resp = json.loads(response.body)

        self.write('enqued job for uid: %d, rand: %d\n' % (resp['uid'],
                resp['rand']))
        self.flush()

        asynch_check_job(self.check_job, resp['uid'])

    @asynchronous
    def check_job(self, uid):
        self.write('checking job for uid: %d...\n' % uid)
        self.flush()

        enqueue_url = 'http://localhost:8888/check/%d' % uid
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(enqueue_url, self.handle_check)

    @asynchronous
    def handle_check(self, response):
        resp = json.loads(response.body)

        if resp['result']:
            self.finish('got result for uid: %d - %s\n' % (resp['uid'],
                    resp['result']))
        else:
            self.write('got status not ready for uid %d\n' % resp['uid'])
            self.flush()
            asynch_check_job(self.check_job, resp['uid'])


class EnqueueAPI(tornado.web.RequestHandler):
    def get(self, rand_param):
        rand = int(rand_param)
        print '/enqueue/%d' % rand
        uid = random.randint(1, 1000000)
        Dreque('localhost').enqueue('queue', func_name, rand=rand, uid=uid)
        self.finish(json.dumps({'uid': uid, 'rand': rand}))


class CheckAPI(tornado.web.RequestHandler):
    def get(self, uid_param):
        uid = int(uid_param)
        print '/check/%d' % uid
        response = {
            'uid': uid,
            'result': StrictRedis().get(uid)
        }
        self.finish(json.dumps(response))


class ResetAPI(tornado.web.RequestHandler):
    def get(self):
        reset_queue()


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/enqueue/(\d+)", EnqueueAPI),
    (r"/check/(\d+)", CheckAPI),
    (r"/reset/?", ResetAPI),
], **{
    'debug': True
})

if __name__ == "__main__":
    reset_queue()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
