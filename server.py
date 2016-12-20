import tornado.ioloop
import tornado.web
import tornado.template as template
import json
port = 8888
quizjsonfile = open("./quizzes.json", "r+")
quiztemplatefile = open("./quiztemplate.html", "r+")
quizjson = json.load(quizjsonfile)['quizzes']
quiztemplate = template.Template(quiztemplatefile.read())
print(quizjson)
def paramsfromrequest(request):
    """ Makes HTTPRequest nice to me"""
    params = request.arguments
    params_dict = {}
    for key, value in request.arguments.items():
        if len(value) == 1:
            params_dict[key] = value[0].decode('UTF-8')
        else:
            params_dict[key] = []
            for part in value:
                params_dict[key].append(part.decode('UTF-8'))
    return params_dict


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class SecondaryHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            self.params = paramsfromrequest(self.request)
            for key, value in list(self.params.items()):
                print("Arg: ",key)
                print("Value: ",value)
            self.write(quiztemplate.generate(quiz=quizjson[self.params["quiz-id"]]))
        except KeyError:
            self.write("Quiz not found")
    def post(self):
        pass
        #TODO: make it add an entry into quizzes.json

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/quiz", SecondaryHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("\n\n\nListening on port " + str(port))
    tornado.ioloop.IOLoop.current().start()
