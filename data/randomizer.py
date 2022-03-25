import csv
import datetime
import json
import random
import re

CATEGORIES = ["Culture", "Fiction", "Food", "History", "People", "Places", "Movies", "News", "Synonyms"]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

MIX = 10000


def get_words(r) -> list:
    return [r[f"Word {i + 1}"] for i in range(4)]


def heuristic(category: str) -> float:
    dists = []
    first, last = None, None
    for i, answer in enumerate(answers):
        if category in answers[answer][2]:
            if last is None:
                first = i
            else:
                dists.append(i - last)

            last = i

    dists.append(first - last + len(answers))
    return sum(map(lambda d: d ** 0.5, dists)) / len(dists)


def sort_key(key: str) -> datetime.datetime:
    d = datetime.datetime.strptime(key + " 2024", "%B %d %Y")
    if d < datetime.datetime(2024, 4, 15):
        d = datetime.datetime.strptime(key + " 2025", "%B %d %Y")

    return d


def score():
    return sum(heuristic(category) for category in CATEGORIES)


def swap(k1: str, k2: str):
    if answers[k1][3] and answers[k2][3]:
        answers[k1], answers[k2] = answers[k2], answers[k1]


answers = {}
ordered = {}

with open("data/answers.csv") as file:
    dates = {(datetime.date(2024, 1, 1) + datetime.timedelta(days=n)).strftime("%B %#d") for n in range(366)}
    for row in csv.DictReader(file):
        if row["Approval"].lower() == "good" and row["Hint"] and all(words := get_words(row)):
            if date := row["Date"]:
                assert date not in answers
                answers[date] = (row["Hint"].replace("\"", ""), words, row["Category"].split(" "), False)
                dates.remove(date)

with open("data/answers.csv") as file:
    for row in csv.DictReader(file):
        if row["Approval"].lower() == "good" and row["Hint"] and all(words := get_words(row)):
            if not row["Date"]:
                date = random.choice(tuple(dates))

                answers[date] = (row["Hint"].replace("\"", ""), words, row["Category"].split(" "), True)
                dates.remove(date)

                if re.match(r'.*? [IVX]+$', row["Hint"]) is not None:
                    *hint, num = row["Hint"].split()
                    hint, num = " ".join(hint), ROMAN.index(num)
                    if hint in ordered:
                        ordered[hint][0].append(date)
                        ordered[hint][1].update({num: answers[date]})
                    else:
                        ordered[hint] = ([date], {num: answers[date]})


answers = dict(sorted(answers.items(), key=lambda p: sort_key(p[0])))
current = score()

for _ in range(MIX):
    a, b = random.choices(list(answers.keys()), k=2)
    swap(a, b)
    if (future := score()) < current:
        swap(a, b)
    else:
        current = future


for hint in ordered:
    for index, entry in enumerate(sorted(ordered[hint][0], key=sort_key)):
        answers[entry] = ordered[hint][1][index]


answers = dict(sorted(((answer, tup[:3]) for answer, tup in answers.items()), key=lambda p: sort_key(p[0])))
with open("data/answers_new.js", "w+") as file:
    string = json.dumps(answers).replace("'", "\\'")
    file.write(f"answers = JSON.parse('{string}')")
