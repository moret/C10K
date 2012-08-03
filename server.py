import json
import tornado.ioloop
import tornado.web
import tornado.httpclient
from tornado.web import asynchronous

search = 'http://search.twitter.com/search.json?q=pythonbrasil&result_type=mixed&count=1'


class MainHandler(tornado.web.RequestHandler):

    @asynchronous
    def get(self):
        self.write("Hello blocking Twitter!\n")
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(search, self.handle_response)

    def handle_response(self, response):
        last_tweet = json.loads(response.body)['results'][0]['text']
        self.finish(last_tweet)

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
