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
        if self.mc_user_answers == None:
            return None
        else:
            result = {}
            for q_num, user_ans in enumerate(self.mc_user_answers):
                for question_ans in self.mc_question_answers:
                    print(user_ans)
                    print(question_ans)
                if user_ans == self.mc_question_answers[q_num]:
                    result[q_num] = [user_ans, True]
                else:
                    result[q_num] = [user_ans, False]
            return result

    def normalize(self, tokens):
        normalized_tokens = []
        for word in tokens:
            if word not in stopwords.words('english'):
                normalized_tokens.append(word)
        return normalized_tokens

    def sa_check(self):
        if self.sa_answers == None:
            return None
        else:
            for x, keylist in enumerate(self.keywords):
                #keylist is list
                self.keywords[x] = self.normalize(keylist)
            self.percent_correct = {}
            # print(self.keywords)
            for q_num, u_ans in enumerate(self.sa_answers):
                # print(u_ans)
                self.u_ans_words = self.normalize(nltk.word_tokenize(u_ans))
                self.num_of_words_in_ans = len(self.u_ans_words)
                self.num_of_words_in_both = 0
                for keyword in self.keywords[q_num]:
                    for word in self.u_ans_words:
                        # print(keyword)
                        if word.lower() == keyword:
                            self.num_of_words_in_both += 1
                #end of checking for keywords in user answer
            self.percent_correct[q_num] = [u_ans, (self.num_of_words_in_both/self.num_of_words_in_ans)*100]
            return self.percent_correct
