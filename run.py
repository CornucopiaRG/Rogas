#coding = utf-8

from backend.application import Application
from backend import config
import tornado.ioloop
import tornado.options
from tornado.options import define, options

define('port', default = config.DEFAULT_PORT, type = int)

def run():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__' :
    run()
