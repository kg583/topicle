import csv
import datetime
import json
import random
import re

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def get_words(r) -> list:
    return [r[f"Word {i + 1}"] for i in range(4)]


def sort_key(key: str) -> datetime.datetime:
    return datetime.datetime.strptime(key + " 2024", "%B %d %Y")


answers = {}
ordered = {}

with open("data/answers.csv") as file:
    dates = {(datetime.date(2024, 1, 1) + datetime.timedelta(days=n)).strftime("%B %#d") for n in range(366)}
    for row in csv.DictReader(file):
        if row["Approval"].lower() == "good" and row["Hint"] and all(words := get_words(row)):
            if date := row["Date"]:
                assert date not in answers
                answers[date] = (row["Hint"].replace("\"", ""), words, row["Category"].split(" "))
                dates.remove(date)

with open("data/answers.csv") as file:
    for row in csv.DictReader(file):
        if row["Approval"].lower() == "good" and row["Hint"] and all(words := get_words(row)):
            if not row["Date"]:
                date = random.choice(tuple(dates))

                answers[date] = (row["Hint"].replace("\"", ""), words, row["Category"].split(" "))
                dates.remove(date)

                if re.match(r'.*? [IVX]+$', row["Hint"]) is not None:
                    *hint, num = row["Hint"].split()
                    hint, num = " ".join(hint), ROMAN.index(num)
                    if hint in ordered:
                        ordered[hint][0].append(date)
                        ordered[hint][1].update({num: answers[date]})
                    else:
                        ordered[hint] = ([date], {num: answers[date]})


for hint in ordered:
    for index, entry in enumerate(sorted(ordered[hint][0], key=sort_key)):
        answers[entry] = ordered[hint][1][index]


answers = dict(sorted(answers.items(), key=lambda p: sort_key(p[0])))
with open("data/answers.js", "w+") as file:
    string = json.dumps(answers).replace("'", "\\'")
    file.write(f"answers = JSON.parse('{string}')")
