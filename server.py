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
    """ Takes in an HTTPRequest object and returns the parameters(the things after the question mark paired by equal signs and separated by ampersands) from the URI"""
    param_string = request.uri.split("?")[1] #gets the part after the question mark as a string
    # print(param_string)
    params_list = param_string.split("&") # gives a list containing every pair=of request=paramaters in=a list=like that
    # print(params_list)
    params_dict = {}
    for pair in params_list: #loops through list and makes every key=value pair into a key: value pair in the dictionary
        key = pair.split("=")[0]
        value = pair.split("=")[1]
        params_dict[key] = value
    # print(params_dict)
    return params_dict


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class SecondaryHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            self.params = paramsfromrequest(self.request)
            self.write(quiztemplate.generate(quiz=quizjson[self.params["quiz-id"]]))
        except KeyError:
            self.write("Quiz not found")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/path", SecondaryHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Listening on port " + str(port))
    tornado.ioloop.IOLoop.current().start()
