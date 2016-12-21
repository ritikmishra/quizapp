import tornado.ioloop
import tornado.web
import tornado.template as template
import json
import random
port = 8888
quizjsonfile = open("./quizzes.json", "r+")
quiztemplatefile = open("./quiztemplate.html", "r+")
quizjson = json.load(quizjsonfile)
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


class AnswerHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.params = paramsfromrequest(self.request)
        for key, value in list(self.params.items()):
            print("Arg: ",key)
            print("Value: ",value)
    def post(self):
        self.write("data recieved")

class MakeQuiz(tornado.web.RequestHandler):
    def prepare(self):
        self.params = paramsfromrequest(self.request)
        for key, value in list(self.params.items()):
            print("Arg: ",key)
            print("Value: ",value)
    def post(self):
        print(self.params)
        self.quizname = random.randrange(0, 999999999999)
        quizjson[self.quizname] = {
            "title": "My Second Quiz",
            "multiple_choice":[{
                    "text": "Is this a mutliple choice question?",
                    "options": ["Yes","No","Perhaps"],
                    "answer": "Yes"
                },
                {
                    "text": "What is microphone?",
                    "options": ["False","True"],
                    "answer": "Yes"
                }],
            "short_answer":[
            {
                "text": "Is this a mutliple choice question?",
                "keywords": ["quiz", "contains", "elements", "both", "multiple", "choice", "short", "answer", "bubbles", "checkbox", "textbox"],
                "answer": "Yes"
            }]
        }

        print(self.quizname)
        self.write(quiztemplate.generate(quiz=quizjson[self.quizname]))
        #TODO: make it add an entry into quizzes.json

class SecondaryHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.params = paramsfromrequest(self.request)
        for key, value in list(self.params.items()):
            print("Arg: ",key)
            print("Value: ",value)
    def get(self):
        try:
            print(self.params["quiz-id"])
            self.write(quiztemplate.generate(quiz=quizjson[self.params["quiz-id"]]))
        except KeyError:
            self.write("Quiz not found")


def make_app():
    return tornado.web.Application([
        (r"/", AnswerHandler),
        (r"/quiz", SecondaryHandler),
        (r"/upload", MakeQuiz),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("\n\n\nListening on port " + str(port))
    tornado.ioloop.IOLoop.current().start()
