#if the submitted answer contains 75% or more of the keywords or a synonym of its keyword, then it is correct. Otherwise, mark wrong.
"""
This module was made for the QuizApp by Ritik Mishra.

It defines the Answer class which has methods for seeing if an answer is correct.
Also has some other useful functions
"""
import json
import nltk
from nltk.corpus import stopwords


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

def stringtojson(words):
        print(words)
        json_acceptable_string = words.replace("'", "\"")

        dictionary = json.loads(json_acceptable_string)
        return dictionary
        # return words

class Answer:
    #
    def __init__(self, keywords, sa_answers, mc_user_answers, mc_question_answers):
        """
        Accepts list of lists 'keywords', list 'sa_answers', list 'mc_user_answers', list 'mc_question_answers'
        """
        self.keywords = keywords
        self.sa_answers = sa_answers
        self.mc_user_answers = mc_user_answers
        self.mc_question_answers = mc_question_answers
        try:
            test = nltk.word_tokenize("Test sentence")
        except LookupError:
            nltk.download("punkt")
        try:
            test = stopwords.words('english')
        except LookupError:
            nltk.download("stopwords")
        #tokenize the answer
    def mc_check(self):
        corrected = {}
        #corrected is a dict of lists.
        #corrected has the structure of
        # {qnum: [user_ans, True/False, correct_ans], qnum: [user_ans, True/False, correct_ans], . . .}
        for key, value in list(self.mc_user_answers.items()):
            key = int(key)
            corrected[key] = [value]
            if value == self.mc_question_answers[key]:
                corrected[key].append(True)
            else:
                corrected[key].append(False)
            corrected[key].append(self.mc_question_answers[key])
        return corrected


    def normalize(self, tokens):
        normalized_tokens = []
        for word in tokens:
            if word not in stopwords.words('english'):
                normalized_tokens.append(word)
        return normalized_tokens

    def sa_check(self):
        print("Checking SA \n ########################")
        print("Keywords:", self.keywords)
        print("Answers:", self.answers)
        if self.keywords != None and self.sa_answers != None:
            try:
                for x, keylist in enumerate(self.keywords):
                    # We remove all stopwords from the keywords list
                    self.keywords[x] = self.normalize(keylist)
                self.percent_correct = {}
                # print(self.keywords)
                for q_num, u_ans in list(self.sa_answers.items()):
                    if u_ans != '':
                        self.u_ans_words = self.normalize(nltk.word_tokenize(u_ans)) #normalize  user answer
                        self.num_of_words_in_ans = len(self.u_ans_words)
                        self.num_of_words_in_both = 0
                        for keyword in self.keywords[q_num]:
                            for word in self.u_ans_words:
                                if word.lower() == keyword.lower():
                                    self.num_of_words_in_both += 1
                        #end of checking for keywords in user answer
                        try:
                            self.percent_correct[q_num] = [u_ans, (self.num_of_words_in_both/self.num_of_words_in_ans)*100] # calculate percentage accuracy
                        except ZeroDivisionError:
                            self.percent_correct[q_num] = [u_ans, (self.num_of_words_in_both)*100] # calculate percentage accuracy
                return self.percent_correct
            except TypeError:
                raise

        else:
            return None
