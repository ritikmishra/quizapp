#if the submitted answer contains 75% or more of the keywords or a synonym of its keyword, then it is correct. Otherwise, mark wrong.
"""
This module was made for the QuizApp by Ritik Mishra.

It defines the Answer class which has methods for seeing if an answer is correct.  
"""

class Answer:
    def __init__(self, keywords, answer):
        """
        Accepts list 'keywords' and string 'answer'. It tokenizes answer, expands contractions and deletes unnecessary words from the tokenization i.e 'the', 'is' will be deleted.
        """
        self.keywords = keywords
        self.answer = answer
        #tokenize the answer
