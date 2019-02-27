import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define,parse_command_line,options
import os
import json

from player import playerHandler
define("port", default=5000, help="run on the given port", type=int)

class indexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

def make_app():
    return tornado.web.Application([
        (r'/',indexHandler),
        (r'/webs',playerHandler),
    ],static_path=os.getcwd(),debug=True)

if __name__ == "__main__":
    parse_command_line()
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)
    print(options.port)
    tornado.ioloop.IOLoop.current().start()
