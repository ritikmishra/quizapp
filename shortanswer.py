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
    def __init__(self, keywords, answer):
        """
        Accepts list 'keywords' and string 'answer'. It tokenizes answer, expands contractions and deletes unnecessary words from the tokenization i.e 'the', 'is' will be deleted.
        """
        self.keywords = keywords
        self.answer = answer
        #tokenize the answer
