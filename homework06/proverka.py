import csv
import string

from bayes import NaiveBayesClassifier

with open("data/SMSSpamCollection", encoding='utf-8') as f:
    data = list(csv.reader(f, delimiter="\t"))


def clean(s):
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)


X, y = [], []
for target, msg in data:
    X.append(msg)
    y.append(target)
X = [clean(x).lower() for x in X]
X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]
model = NaiveBayesClassifier(alpha=0.05)
print(model.fit(X_train, y_train))
print(model.predict(X_test))
print(X_test)
print(y_test)
print(model.score(X_test,y_test))
