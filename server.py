import json
import tornado.ioloop
import tornado.web
import tornado.httpclient

search = 'http://search.twitter.com/search.json?q=pythonbrasil&result_type=mixed&count=1'

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello blocking Twitter!\n")
        http_client = tornado.httpclient.HTTPClient()
        response = http_client.fetch(search)
        last_tweet = json.loads(response.body)['results'][0]['text']
        self.write(last_tweet)

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
