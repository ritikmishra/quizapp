# Import the tornado module, that allows us to run a webserver
# Tornado was written by FriendFeed, and development is largely continued by Ben Darnell.
import tornado.ioloop
import tornado.web
import tornado.template as template

# Import the JSON module to manipulate quizzes.json, the os module to read environment variables, and random to generate a random number
# Those modules come with python
import json
import os
import random

# Import the algorithms that were moved to algorithms.py to manage complexity
from algorithms import *

# Set up variables needed to start the server
try:
    port = os.environ['PORT']
except KeyError:
    port = 8888
try:
    url = os.environ['URL']
except KeyError:
    url = "http://localhost:" + str(port)
quizjson = importfile()
templateloader = template.Loader("./templates")


class AnswerHandler(tornado.web.RequestHandler):
    """
    This handler handles requests to the /checkanswer path. This allows the user to check the answer on their quiz.
    """
    def prepare(self):
        """
        Prepare for handling the request
        """
        self.params = paramsfromrequest(self.request)
        self.quizjson = importfile()
    def post(self):
        """
        Handle a post request made to /checkanswer
        The quiz answers are sent to /checkanswer via a POST request
        """

        # Define variables
        self.user_mc_ans = {}
        self.q_mc_ans = []
        self.q_sa_keywords = []
        self.user_sa_ans = {}

        # Add values to the dicts for user answers
        for key, value in list(self.params.items()):
            if key != 'quiz-id':
                if key[0:2] == 'mc':
                    self.user_mc_ans[int(key[2:])] = value
                elif key[0:2] == 'sa':
                    self.user_sa_ans[int(key[2:])] = value
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
        self.checked_mc = self.checkans.mc_check()
        self.checked_sa = self.checkans.sa_check()

        print("Short Answer questions \n ###############################")
        print(self.checked_sa)
        print("Multiple Choice questions \n ###############################")
        print(self.checked_mc)

        self.write(templateloader.load("answertemplate.html").generate(url=url,quiz=self.quizjson[self.params["quiz-id"]],id=self.params["quiz-id"],mc_answers=self.checked_mc,sa_answers=self.checked_sa))
class NewQuizHandler(tornado.web.RequestHandler):
    """
    This handler handles requests to the /upload path.
    The user can upload their own quizzes by sending a POST request to /upload
    """
    def prepare(self):
        """
        Prepare for handling the request
        """
        self.params = paramsfromrequest(self.request)
        self.quizjson = importfile()
        print(self.params)
        try:
            self.api = stringtobool(self.params['api'])
        except (KeyError, TypeError):
            self.api = True
        try:
            self.prepared = stringtobool(self.params['prepared'])
        except (KeyError, TypeError):
            self.prepared = True
        try:
            self.done = stringtobool(self.params['done'])
        except (KeyError, TypeError):
            self.done = False
        print(self.params)
    def get(self):
        self.write(templateloader.load("quizpreuploadtemplate.html").generate(url=url))
    def post(self):
        """
        Actually handle the request
        """
        if self.api:
            try:
                self.quizdata = stringtojson(self.params["quiz"])
                self.quizid = random.randrange(0, 999999999999)
                self.seentitle = False
                for key, value in list(self.quizdata.items()):
                    print(key)
                    if key == "title":
                        self.seentitle = True
                if self.seentitle:
                    self.quizjson[self.quizid] = self.quizdata
                    with open("./quizzes.json", "w") as quizjsonfile:
                        quizjsonfile.truncate()
                        json.dump(self.quizjson, quizjsonfile, ensure_ascii=True, indent=4, separators=(',', ': '))
                        quizjsonfile.close()
                    self.quizjson = importfile()
                    print(self.quizjson)
                    self.redirect("https://codebreakquizapp.herokuapp.com/quiz?quiz-id=" + str(self.quizid))
                elif not self.seentitle:
                    self.write("Your quiz has no title, so we did not upload it to our server. ")
            except KeyError:
                self.write("We did not detect a quiz. Make sure that it was sent under the parameter of 'quiz'. Also, because you're using the API, there is no need to POST a number of multiple choice questions and short answer questions.")
        elif not self.api and not self.prepared:
            self.write(templateloader.load("quizpreuploadtemplate.html").generate(url=url))
        elif not self.api and self.prepared:
            try:
                self.num_of_mc = int(self.params['nummc'])
            except ValueError:
                self.num_of_mc = 0
            try:
                self.num_of_sa = int(self.params['numsa'])
            except ValueError:
                self.num_of_sa = 0
            try:
                self.num_of_mco = int(self.params['nummco'])
            except ValueError:
                self.num_of_mco = 0
            self.write(templateloader.load("quizuploadtemplate.html").generate(url=url,num_of_mc=self.num_of_mc,num_of_sa=self.num_of_sa,num_of_mco=self.num_of_mco))

class QuizHandler(tornado.web.RequestHandler):
    """
    Handle requests to the /quiz path
    """
    def prepare(self):
        """
        Prepare for handling the request by checking if there is a quiz-id parameter
        """
        self.params = paramsfromrequest(self.request)
        self.quizjson = importfile()
        try:
            print(self.params["quiz-id"])
        except KeyError:
            self.params['quiz-id'] = None
        finally:
            print(self.request.arguments)

    def get(self):
        """
        Handle the request by sending the quiz page if it exists, a search page if no quiz ID was specified, and a 'Quiz not found' page if the quiz was not found
        """
        if self.params['quiz-id'] == None:
            self.write(templateloader.load("quizidsearchtemplate.html").generate(url=url))
        else:
            try:
                self.write(templateloader.load("quiztemplate.html").generate(url=url,quiz=self.quizjson[self.params["quiz-id"]],id=self.params["quiz-id"]))
            except KeyError:
                self.write(templateloader.load("quiznotfoundtemplate.html").generate(url=url,err="We were unable to find that quiz"))
class MainPageRedirHandler(tornado.web.RequestHandler):
    """
    Redirect all requests made to the path / to the path /home
    """
    def get(self):
        self.redirect("/home", permanent=True)
class MainPageHandler(tornado.web.RequestHandler):
    """
    Generate a home page with all the quizzes to display to the user
    """
    def get(self):
        self.quizjson = importfile()

        self.write(templateloader.load("mainpagetemplate.html").generate(url=url,quizzes=self.quizjson))

# All code below this point is from the tutorial on how to use Tornado or largely inspired by it
# The turorial is found at found at http://www.tornadoweb.org/en/stable/
def make_app():
    """Assign each handler to the path that they handle"""
    return tornado.web.Application([
        (r"/checkanswer", AnswerHandler),
        (r"/quiz", QuizHandler),
        (r"/upload", NewQuizHandler),
        (r"/", MainPageRedirHandler),
        (r"/home", MainPageHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(port)
    print("\n\n\nListening on port " + str(port))
    tornado.ioloop.IOLoop.current().start()
