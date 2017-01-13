#if the submitted answer contains 75% or more of the keywords or a synonym of its keyword, then it is correct. Otherwise, mark wrong.
"""
This module was made for the QuizApp by Ritik Mishra.

It defines the Answer class which has methods for seeing if an answer is correct.
Also has some other useful functions
"""
import json
import tornado.template as template
import nltk
from nltk.corpus import stopwords
def stringtobool(var):
    if var.lower() == "true":
        return True
    elif var.lower() == "false":
        return False
    else:
        raise TypeError('The input value must be \'True\' or \'False\' as strings')
def import_quizzes_json():
    with open("./quizzes.json", "r+") as item:
        return json.load(item)
        item.close()

def paramsfromrequest(request):
    """Changes the format of the HTTP request parameters so that they may be more easily used"""
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

def stringtojson(words):
    """Converts the string representation of some JSON data to a dictionary"""
    json_acceptable_string = words.replace("'", "\"")
    dictionary = json.loads(json_acceptable_string)
    # return words
    return dictionary


class Answer:
    """
    Used in main.py in the AnswerHandler class to check the answers of a user who has taken a quiz
    """
    def __init__(self, keywords, sa_answers, mc_user_answers, mc_question_answers):
        """
        keywords: a list of lists. Each list in the list will contain keywords, which will be present in a correct short answer question
        sa_answers: The list of written answers that the user submitted
        mc_user_answers: A list of the multiple choice answers that the user picked
        mc_question_answers: A list of the multiple choice answers that are the correct answers
        """
        self.keywords = keywords
        self.sa_answers = sa_answers
        self.mc_user_answers = mc_user_answers
        self.mc_question_answers = mc_question_answers

        # Check if we need to download the punkt tokenizer
        try:
            test = nltk.word_tokenize("Test sentence")
        except LookupError:
            nltk.download("punkt")
        # Check if we need to download the stopwords corpus
        try:
            test = stopwords.words('english')
        except LookupError:
            nltk.download("stopwords")

    def mc_check(self):
        """Check if the user answers for the multiple choice questions are correct"""
        # self.corrected is a dict of lists.
        # Each list will contain the following items in the specified order:
        # What the user picked(string), if they got it right(bool), what the correct answer was(string)
        self.corrected = {}

        # If self.mc_user_answers is None, then an AttributeError will be thrown
        # We catch the error so that having multiple choice questions in a quiz will not be necessary
        try:
            for key, value in list(self.mc_user_answers.items()):
                key = int(key)
                self.corrected[key] = [value]
                if value == self.mc_question_answers[key]:
                    self.corrected[key].append(True)
                else:
                    self.corrected[key].append(False)
                self.corrected[key].append(self.mc_question_answers[key])
            return self.corrected
        except AttributeError:
            return None

    def normalize(self, tokens):
        normalized_tokens = []
        # The following for loop inspired by Darren Thomas's answer to this StackOverflow question
        # https://stackoverflow.com/questions/5486337/how-to-remove-stop-words-using-nltk-or-python
        for word in tokens:
            if word not in stopwords.words('english'):
                normalized_tokens.append(word)
        return normalized_tokens

    def sa_check(self):
        if self.keywords != None and self.sa_answers != None:
            try:
                for x, keylist in enumerate(self.keywords):
                    # We remove all stopwords from the keywords list and do it for all such lists in self.keywords
                    self.keywords[x] = self.normalize(keylist)
                self.percent_correct = {}
                for q_num, u_ans in list(self.sa_answers.items()):
                    # for each answer
                    if u_ans != '':
                        self.u_ans_words = self.normalize(nltk.word_tokenize(u_ans)) #normalize  user answer
                        self.num_of_words_in_both = 0
                        for word in self.u_ans_words:
                            for keyword in self.keywords[q_num]:
                                if (word.lower() == keyword.lower()):
                                    self.num_of_words_in_both += 1
                        #end of checking for keywords in user answer
                        try:
                            # If the answer is one letter, self.num_of_words_in_ans will be 0
                            # so a ZeroDivisionError is thrown. We catch the error and handle it
                            self.percent_correct[q_num] = [u_ans, (self.num_of_words_in_both/len(self.keywords[q_num]))*100] # calculate percentage accuracy
                        except ZeroDivisionError:
                            self.percent_correct[q_num] = [u_ans, (self.num_of_words_in_both)*100] # calculate percentage accuracy
                return self.percent_correct
            except TypeError:
                raise

        else:
            return None
