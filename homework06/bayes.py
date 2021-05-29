import math
import string

class NaiveBayesClassifier:

    def __init__(self, alpha):
    	self.alpha = alpha
        self.count_statuses = []
        self.status_word = {}
        self.y_set = []
        self.final_result = []
        pass

    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y. """
        list_of_criteria = []
        y_set = list(set(y))
        self.y_set = y_set
        y_len_mark = len(y_set)
        status_word = {}
        self.count_statuses = [0 for _ in range(y_len_mark)]
        for message, mark in zip(X, y):
            for i, value in enumerate(y_set):
                if mark == value:
                    self.count_statuses[i] += 1
            word_list = message.split(" ")
            for word in word_list:
                if word not in status_word:
                    status_word[word] = [0 for _ in range(y_len_mark * 2)]
                for i, value in enumerate(y_set):
                    if mark == value:
                        status_word[word][i] += 1
        all_words = len(status_word)
        criteria_counter = [0 for _ in range(y_len_mark)]
        for key in status_word:
            list_of_statuses = status_word[key]
            for i in range(y_len_mark):
                criteria_counter[i] += list_of_statuses[i]
        for key in status_word:
            list_of_statuses = status_word[key]
            for i in range(y_len_mark, len(list_of_statuses)):
                list_of_statuses[i] = float((list_of_statuses[i - y_len_mark] + self.alpha) / (
                        criteria_counter[i - y_len_mark] + self.alpha * all_words))
        self.status_word = status_word
        for i in range(len(self.count_statuses)):
            self.count_statuses[i] = self.count_statuses[i] / len(y)
        return status_word

    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        for message in X:
            result = 0
            winner = 0
            for i in range(len(self.y_set)):
                lnp = math.log(self.count_statuses[i])
                word_list = message.split(" ")
                ln_sum = lnp
                for word in word_list:
                    if word in self.status_word:
                        ln_sum += math.log(self.status_word[word][i + len(self.y_set)])
                    else:
                        ln_sum += 0
                if i == 0:
                    result = ln_sum
                if ln_sum > result:
                    result = ln_sum
                    winner = i
            self.final_result.append([message, self.y_set[winner]])
        return self.final_result

    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        all_len = len(X_test)
        same_results = 0
        for message, mark in zip(X_test, y_test):
            for el in self.final_result:
                if el[0]==message:
                    if el[1] == mark:
                        same_results += 1
                        break
        return same_results / all_len
        
def clean(s):
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)

