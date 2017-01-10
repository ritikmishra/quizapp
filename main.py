# Import the tornado module, that allows us to run a webserver
# Tornado was written by FriendFeed, and development is largely continued by Ben Darnell.
import tornado.ioloop
import tornado.web
import tornado.template as template
# Import the JSON library to handle quizzes.json. It is an included python module.
import json
# Import the os library to check for environment variable. It is an included python module.
import os
# Import the random library to assign a unique quiz ID to newly uploaded quizzes. It is an included python module.
import random

# Import the algorithms moved to algorithms.py
from algorithms import paramsfromrequest, stringtojson, Answer, importfile

# Check to see if the machine has a preferred port for checking the server
try:
    port = os.environ['PORT']
except KeyError:
    port = 8888
# Check to see if the machine has a preferred URL for the server
try:
    url = os.environ['URL']
except KeyError:
    url = "http://localhost:" + str(port)

# Move webpage templates into a baseloader so we may serve them later
quizjson = importfile("./quizzes.json", isjson=True)
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

        # We catch the KeyError exception because it will be thrown if the user does not answer the multiple choice questions
        try:
            for question in list(self.quizjson[self.params["quiz-id"]]['multiple_choice']):
                self.q_mc_ans.append(question["answer"])
        except KeyError:
            self.q_mc_ans = None

        # We catch the KeyError exception because it will be thrown if the user does not answer the short answer questions
        try:
            for question in list(self.quizjson[self.params["quiz-id"]]['short_answer']):
                self.q_sa_keywords.append(question["keywords"])
        except KeyError:
            self.q_sa_keywords = None

        # Create an instance of the Answer class to check the user answers. Its code is found in algorithms.py
        self.checkans = Answer(self.q_sa_keywords, self.user_sa_ans, self.user_mc_ans, self.q_mc_ans)
        self.checked_mc = self.checkans.mc_check()
        self.checked_sa = self.checkans.sa_check()

        # Logging on the server for debugging purposes
        print("Short Answer questions \n ###############################")
        print(self.checked_sa)
        print("Multiple Choice questions \n ###############################")
        print(self.checked_mc)

        # Serve the answer page to the user
        self.write(templateloader.load("answertemplate.html").generate(url=url,quiz=self.quizjson[self.params["quiz-id"]],id=self.params["quiz-id"],mc_answers=self.checked_mc,sa_answers=self.checked_sa))
class NewQuizHandler(tornado.web.RequestHandler):
    """
    This handler handles requests to the /upload path. This allows the user to upload their own quizzes
    """
    def prepare(self):
        """
        Prepare for handling the request
        """
        self.params = paramsfromrequest(self.request)
        # Read quizzes.json
        self.quizjson = importfile("./quizzes.json", isjson=True)
        print(self.quizjson)
        # Check if the request was sent from our UI or our
        try:
            self.api = self.params['api']
        except KeyError:
            self.api = True
    def post(self):
        # Check if a post request was made directly to /upload or if the webpage was used
        if api:
            # We want to catch the KeyError because a 500 Error message would be sent if the user does not upload the data under the correct parameter
            try:
                # Assign the quiz an ID and check for a quiz title
                self.quizdata = stringtojson(self.params["quiz"])
                self.quizid = random.randrange(0, 999999999999)
                self.seentitle = False
                for key, value in list(self.quizdata.items()):
                    print(key)
                    if key == "title":
                        self.seentitle = True
                if self.seentitle:
                    # Logging to asssist debugging
                    print("New quiz uploaded: " + str(self.quizid) + " \n ###############")
                    print(self.quizdata)
                    # Add new quiz to our dictionary for quizzes and write it to quizzes.json
                    self.quizjson[self.quizid] = self.quizdata
                    with open("./quizzes.json", "w") as quizjsonfile:
                        json.dump(self.quizjson, quizjsonfile, ensure_ascii=False)
                        quizjsonfile.close()
                    # Send the user to their newly created quiz
                    self.redirect("https://codebreakquizapp.herokuapp.com/quiz?quiz-id=" + str(self.quizid))
                elif not self.seentitle:
                    # Remind the user if they had no title
                    self.write("Your quiz has no title, so we did not upload it to our server. ")
            except KeyError:
                # Remind the user if we did not find a quiz
                self.write("We did not detect a quiz. Make sure that it was sent under the parameter of 'quiz'.")
class QuizHandler(tornado.web.RequestHandler):
    """
    Handle requests to the /quiz path
    """
    def prepare(self):
        """
        Prepare for handling the request by checking if there is a quiz-id parameter
        """
        self.params = paramsfromrequest(self.request)
        self.quizjson = importfile("./quizzes.json", isjson=True)
        try:
            print(self.params["quiz-id"])
        except KeyError:
            self.params['quiz-id'] = None
        finally:
            print(self.request.arguments)
            print(self.quizjson)
    def get(self):
        """
        Handle the request by sending the quiz page if it exists, a search page if no quiz ID was specified, and a 'Quiz not found' page if the quiz was not found
        """
        if self.params['quiz-id'] == None:
            self.write(templateloader.load("quizsearchtemplate.html").generate(url=url))
        else:
            try:
                self.write(templateloader.load("quiztemplate.html").generate(url=url,quiz=self.quizjson[self.params["quiz-id"]],id=self.params["quiz-id"]))
            except KeyError:
                self.write(templateloader.load("quiznotfoundtemplate.html").generate(url=url))
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
        self.quizjson = importfile("./quizzes.json", isjson=True)
        print(self.quizjson)
        self.write(templateloader.load("mainpagetemplate.html").generate(url=url,quizzes=self.quizjson))

# All code below this point is from the tutorial on how to use Tornado or largely inspired by it
# The turorial is found at found at http://www.tornadoweb.org/en/stable/
def make_app():
    """Assign each handler to the path that they handle"""
    return tornado.web.Application([
        (r"/checkanswer", AnswerHandler),
        (r"/quiz", QuizHandler),
        (r"/upload", NewQuizHandler),
        #(r"/uploadUI", NewQuizFromPageHandler),
        (r"/", MainPageRedirHandler),
        (r"/home", MainPageHandler),
    ])

# Check if this is being imported as a module. If not, then start the server
if __name__ == "__main__":
    app = make_app()
    app.listen(port)
    print("\n\n\nListening on port " + str(port))
    tornado.ioloop.IOLoop.current().start()
