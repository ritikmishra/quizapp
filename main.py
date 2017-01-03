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

# get all the files into our variables
with open("./quizzes.json", "r+") as quizjsonfile:
    quizjson = json.load(quizjsonfile)
    quizjsonfile.close()
with open("./quiztemplate.html", "r+") as quiztemplatefile:
    quiztemplate = template.Template(quiztemplatefile.read())
    quiztemplatefile.close()
with open("./answertemplate.html", "r+") as quiztemplatefile:
    answertemplate = template.Template(quiztemplatefile.read())
    quiztemplatefile.close()
with open("./mainpagetemplate.html", "r+") as quiztemplatefile:
    mainpagetemplate = template.Template(quiztemplatefile.read())
    quiztemplatefile.close()
with open("./quiznotfoundtemplate.html", "r+") as quiztemplatefile:
    quiznotfoundtemplate = template.Template(quiztemplatefile.read())
    quiztemplatefile.close()
with open("./quizidsearchtemplate.html", "r+") as quiztemplatefile:
    quizsearchtemplate = template.Template(quiztemplatefile.read())
    quiztemplatefile.close()




class AnswerHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.params = paramsfromrequest(self.request)
        print("Answer Check Params \n #############################")
        print(self.params)
    def post(self):
        user_mc_ans = {}
        q_mc_ans = []
        q_sa_keywords = []
        user_sa_ans = {}
        for key, value in list(self.params.items()):
            if key != 'quiz-id':
                if key[0:2] == 'mc':
                    user_mc_ans[int(key[2:])] = value
                elif key[0:2] == 'sa':
                    user_sa_ans[int(key[2:])] = value
        try:
            for question in list(quizjson[self.params["quiz-id"]]['multiple_choice']):
                q_mc_ans.append(question["answer"])
        except KeyError:
            q_mc_ans = None
        try:
            for question in list(quizjson[self.params["quiz-id"]]['short_answer']):
                q_sa_keywords.append(question["keywords"])
        except KeyError:
            q_sa_keywords = None
        self.checkans = Answer(q_sa_keywords, user_sa_ans, user_mc_ans, q_mc_ans)
        print(user_sa_ans)
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

    def post(self):
        try:
            self.quizdata = stringtojson(self.params["quiz"])
            self.quizid = random.randrange(0, 999999999999)
            seentitle = False
            for key, value in list(self.quizdata.items()):
                #check if there is a quiz title
                print(key)
                if key == "title":
                    seentitle = True
            if seentitle:
                print("New quiz uploaded: " + str(self.quizid) + " \n ###############")
                print(self.quizdata)
                quizjson[self.quizid] = self.quizdata
                with open("./quizzes.json", "r+") as quizjsonfile:
                    json.dump(quizjson, quizjsonfile, sort_keys=True, indent=4, separators=(',', ': '))
                self.redirect("https://codebreakquizapp.herokuapp.com/quiz?quiz-id=" + str(self.quizid))
            elif not seentitle:
                self.write("Your quiz has no title, so we did not upload it to our server. ")
        except KeyError:
            self.write("We did not detect a quiz. Make sure that it was sent under the parameter of 'quiz'.")
        except Exception as err:
            self.responsestr = "We were unable to process your request. Here are the error details:"
            for e in list(err.args):
                self.responsestr = self.responsestr + " " + e + "\n"
            self.write(self.responsestr)
            raise
class SecondaryHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.params = paramsfromrequest(self.request)
        try:
            print(self.params["quiz-id"])
        except KeyError:
            self.params['quiz-id'] = None

        print(self.request.arguments)
    def get(self):
        if self.params['quiz-id'] == None:
            self.write(quizsearchtemplate.generate())
        else:
            try:
                self.write(quiztemplate.generate(quiz=quizjson[self.params["quiz-id"]],id=self.params["quiz-id"]))
            except KeyError:
                self.write(quiznotfoundtemplate.generate())
class MainPageRedirHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/home", permanent=True)
class MainPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(mainpagetemplate.generate(quizzes=quizjson))

def make_app():
    return tornado.web.Application([
        (r"/checkanswer", AnswerHandler),
        (r"/quiz", SecondaryHandler),
        (r"/upload", MakeQuiz),
        (r"/", MainPageRedirHandler),
        (r"/home", MainPageHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(port)
    print("\n\n\nListening on port " + str(port))
    tornado.ioloop.IOLoop.current().start()
