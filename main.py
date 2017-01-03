import tornado.ioloop
import tornado.web
import tornado.template as template
import json
import os
import random
from shortanswer import paramsfromrequest
from shortanswer import stringtojson
from shortanswer import Answer
try:
    port = os.environ['PORT']
except KeyError:
    port = 8888

with open("./quizzes.json", "r+") as quizjsonfile:
    quizjson = json.load(quizjsonfile)
with open("./quiztemplate.html", "r+") as quiztemplatefile:
    quiztemplate = template.Template(quiztemplatefile.read())
with open("./answertemplate.html", "r+") as quiztemplatefile:
    answertemplate = template.Template(quiztemplatefile.read())
with open("./mainpagetemplate.html", "r+") as quiztemplatefile:
    mainpagetemplate = template.Template(quiztemplatefile.read())



class AnswerHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.params = paramsfromrequest(self.request)
    def post(self):
        user_mc_ans = []
        q_mc_ans = []
        q_sa_keywords = []
        user_sa_ans = []
        for key, value in list(self.params.items()):
            if key != 'quiz-id':

                if key[0:2] == 'mc':
                    user_mc_ans.append(value)
                elif key[0:2] == 'sa':
                    user_sa_ans.append(value)
        for question in list(quizjson[self.params["quiz-id"]]['multiple_choice']):
            q_mc_ans.append(question["answer"])
        for question in list(quizjson[self.params["quiz-id"]]['short_answer']):
            q_sa_keywords.append(question["keywords"])
        self.checkans = Answer(q_sa_keywords, user_sa_ans, user_mc_ans, q_mc_ans)
        # print(user_mc_ans)
        # print(q_mc_ans)
        self.checked_mc = self.checkans.mc_check()
        self.checked_sa = self.checkans.sa_check()
        print("Short Answer questions \n ###############################")
        print(self.checked_sa)
        print("Multiple Choice questions \n ###############################")
        print(self.checked_mc)
        self.write(answertemplate.generate(quiz=quizjson[self.params["quiz-id"]],id=self.params["quiz-id"],mc_answers=self.checked_mc,sa_answers=self.checked_sa))

class MakeQuiz(tornado.web.RequestHandler):
    def prepare(self):
        self.params = paramsfromrequest(self.request)

        for key, value in list(self.params.items()):
            print("Arg: ",key)
            print("Value: ",value)

        self.quizdata = stringtojson(self.params["quiz"])
    def get(self):
        self.write()
    def post(self):
        self.quizname = random.randrange(0, 999999999999)
        print(self.quizdata)
        seentitle = False
        for key, value in list(self.quizdata.items()):
            print(key)
            if key == "title":
                seentitle = True
                quizjson[self.quizname] = self.quizdata
                print(self.quizname)
                with open("./quizzes.json", "w") as quizjsonfile:
                    print(quizjson)
                    quizjsonfile.write(json.dumps(quizjson, indent=4, separators=(',', ': ')))
                self.write(quiztemplate.generate(quiz=quizjson[self.quizname],id=self.quizname))
        if not seentitle:
            self.write("Your quiz has no title, so we did not upload it to our server. ")

class SecondaryHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.params = paramsfromrequest(self.request)
        print(self.request.arguments)

    def get(self):
        try:
            print(self.params["quiz-id"])
            self.write(quiztemplate.generate(quiz=quizjson[self.params["quiz-id"]],id=self.params["quiz-id"]))
        except KeyError:
            self.write("That quiz was not found.")

class MainPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(mainpagetemplate.generate(quizzes=quizjson))
        
def make_app():
    return tornado.web.Application([
        (r"/checkanswer", AnswerHandler),
        (r"/quiz", SecondaryHandler),
        (r"/upload", MakeQuiz),
        (r"/", MainPageHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(port)
    print("\n\n\nListening on port " + str(port))
    tornado.ioloop.IOLoop.current().start()
