# Import the tornado module, that allows us to run a webserver
# Tornado was written by Friendfeed, and development is continued by
import tornado.ioloop
import tornado.web
import tornado.template as template
# Import the JSON library to handle quizzes.json
# This library was written by
import json
# Import the os library to check for environment variables
# This library was written by
import os
# Import the random library to assign a unique quiz ID to newly uploaded quizzes
# This library was written by
import random
# Import the algorithms moved to algorithms.py to free up space in this file
from algorithms import paramsfromrequest
from algorithms import stringtojson
from algorithms import Answer

# Check to see if the machine has a preferred port for checking the server
try:
    port = os.environ['PORT']
except KeyError:
    port = 8888

# Move webpage templates into variables so we may serve them later
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
    """
    This handler handles requests to the /checkanswer path. This allows the user to check the answer on their quiz.
    """
    def prepare(self):
        """
        Prepare for handling the request
        """
        self.params = paramsfromrequest(self.request)
        with open("./quizzes.json", "r+") as quizjsonfile:
            self.quizjson = json.load(quizjsonfile)
            quizjsonfile.close()
        print(self.quizjson)
    def post(self):
        """Handle a post request made to /checkanswer"""

        # Prepare variables
        self.user_mc_ans = {}
        self.q_mc_ans = []
        self.q_sa_keywords = []
        self.user_sa_ans = {}

        # Go through the sent data
        for key, value in list(self.params.items()):
            if key != 'quiz-id':
                # Add multiple choice answers (indicated with the first 2 letters of 'mc') to self.user_mc_ans
                if key[0:2] == 'mc':
                    self.user_mc_ans[int(key[2:])] = value
                # Add written answers (indicated with the first 2 letters of 'sa') to self.user_sa_ans
                elif key[0:2] == 'sa':
                    self.user_sa_ans[int(key[2:])] = value
        # We use
        try:
            for question in list(self.quizjson[self.params["quiz-id"]]['multiple_choice']):
                self.q_mc_ans.append(question["answer"])
        except KeyError:
            self.q_mc_ans = None

        try:
            for question in list(self.quizjson[self.params["quiz-id"]]['short_answer']):
                self.q_sa_keywords.append(question["keywords"])
        except KeyError:
            self.q_sa_keywords = None

        self.checkans = Answer(self.q_sa_keywords, self.user_sa_ans, self.user_mc_ans, self.q_mc_ans)
        print(self.user_sa_ans)
        # print(q_mc_ans)
        self.checked_mc = self.checkans.mc_check()
        self.checked_sa = self.checkans.sa_check()

        print("Short Answer questions \n ###############################")
        print(self.checked_sa)
        print("Multiple Choice questions \n ###############################")
        print(self.checked_mc)
        self.write(answertemplate.generate(quiz=self.quizjson[self.params["quiz-id"]],id=self.params["quiz-id"],mc_answers=self.checked_mc,sa_answers=self.checked_sa))
class NewQuizHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.params = paramsfromrequest(self.request)
        with open("./quizzes.json", "r+") as quizjsonfile:
            self.quizjson = json.load(quizjsonfile)
            quizjsonfile.close()
        print(self.quizjson)
    def post(self):
        try:
            self.quizdata = stringtojson(self.params["quiz"])
            self.quizid = random.randrange(0, 999999999999)
            self.seentitle = False
            for key, value in list(self.quizdata.items()):
                #check if there is a quiz title
                print(key)
                if key == "title":
                    self.seentitle = True
            if self.seentitle:
                print("New quiz uploaded: " + str(self.quizid) + " \n ###############")
                print(self.quizdata)
                self.quizjson[self.quizid] = self.quizdata
                with open("./quizzes.json", "w") as quizjsonfile:
                    json.dump(self.quizjson, quizjsonfile, ensure_ascii=False)
                    quizjsonfile.close()
                self.redirect("https://codebreakquizapp.herokuapp.com/quiz?quiz-id=" + str(self.quizid))
            elif not self.seentitle:
                self.write("Your quiz has no title, so we did not upload it to our server. ")
        except KeyError:
            self.write("We did not detect a quiz. Make sure that it was sent under the parameter of 'quiz'.")
class QuizHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.params = paramsfromrequest(self.request)
        try:
            print(self.params["quiz-id"])
        except KeyError:
            self.params['quiz-id'] = None
        finally:
            print(self.request.arguments)
            with open("./quizzes.json", "r+") as quizjsonfile:
                self.quizjson = json.load(quizjsonfile)
                quizjsonfile.close()
            print(self.quizjson)
    def get(self):
        if self.params['quiz-id'] == None:
            self.write(quizsearchtemplate.generate())
        else:
            try:
                self.write(quiztemplate.generate(quiz=self.quizjson[self.params["quiz-id"]],id=self.params["quiz-id"]))
            except KeyError:
                self.write(quiznotfoundtemplate.generate())
class MainPageRedirHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/home", permanent=True)
class MainPageHandler(tornado.web.RequestHandler):
    def get(self):
        with open("./quizzes.json", "r+") as quizjsonfile:
            self.quizjson = json.load(quizjsonfile)
            quizjsonfile.close()
        print(self.quizjson)
        self.write(mainpagetemplate.generate(quizzes=self.quizjson))

def make_app():
    """Assign each handler to the path that they handle"""
    return tornado.web.Application([
        (r"/checkanswer", AnswerHandler),
        (r"/quiz", QuizHandler),
        (r"/upload", NewQuizHandler),
        (r"/", MainPageRedirHandler),
        (r"/home", MainPageHandler),
    ])

# Check if this is being imported as a module. If not, then start the server
# The following code is from the tutorial on how to use Tornado, found at http://www.tornadoweb.org/en/stable/
if __name__ == "__main__":
    app = make_app()
    app.listen(port)
    print("\n\n\nListening on port " + str(port))
    tornado.ioloop.IOLoop.current().start()
