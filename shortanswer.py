#if the submitted answer contains 75% or more of the keywords or a synonym of its keyword, then it is correct. Otherwise, mark wrong.
"""
This module was made for the QuizApp by Ritik Mishra.

It defines the Answer class which has methods for seeing if an answer is correct.
Also has some other useful functions
"""
import json

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
    #keywords, sa_answers,
    def __init__(self, mc_user_answers, mc_question_answers):
        """
        Accepts list of lists 'keywords', list 'sa_answers', list 'mc_user_answers', list 'mc_question_answers'
        """
        # self.keywords = keywords
        # self.sa_answers = sa_answers
        self.mc_user_answers = mc_user_answers
        self.mc_question_answers = mc_question_answers
        #tokenize the answer
    def mc_check(self):
        result = {}
        for q_num, user_ans in enumerate(self.mc_user_answers):
            for question_ans in self.mc_question_answers:
                if user_ans == question_ans:
                    result[q_num] = True
                else:
                    result[q_num] = False
        return result
