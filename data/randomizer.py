import csv
import datetime
import json
import random
import re

CATEGORIES = ["Culture", "Fiction", "Food", "History", "People", "Places", "Movies", "News", "Ordered", "Synonyms"]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

MIX = 10000


def get_words(r) -> list[str]:
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
    d = datetime.datetime.strptime(key + " 2023", "%B %d %Y")
    if d < datetime.datetime(2023, 5, 1):
        d = datetime.datetime.strptime(key + " 2024", "%B %d %Y")

    return d


def score() -> float:
    return sum(heuristic(category) for category in CATEGORIES)


def swap(k1: str, k2: str) -> None:
    if answers[k1][3] and answers[k2][3]:
        answers[k1], answers[k2] = answers[k2], answers[k1]


def tup(r, free: bool) -> tuple[str, list[str], list[str], bool]:
    return r["Topic"].replace("\"", ""), get_words(r), r["Category"].split(" "), free


answers = {}
ordered = {}

# Fixed dates
with open("data/answers.csv") as file:
    dates = {(datetime.date(2024, 1, 1) + datetime.timedelta(days=n)).strftime("%B %#d") for n in range(366)}
    n = 0
    for row in csv.DictReader(file):
        if date := row["Date"]:
            assert date not in answers
            answers[date] = tup(row, False)
            dates.remove(date)

        n += 1
        if n == 366:
            break

# Remaining puzzles
with open("data/answers.csv") as file:
    n = 0
    for row in csv.DictReader(file):
        if not row["Date"]:
            date = random.choice(tuple(dates))

            answers[date] = tup(row, True)
            dates.remove(date)

            if re.match(r'.*? [IVX]+$', row["Topic"]) is not None:
                *topic, num = row["Topic"].split()
                topic, num = " ".join(topic), ROMAN.index(num)
                if topic in ordered:
                    ordered[topic][0].append(date)
                    ordered[topic][1].update({num: answers[date]})
                else:
                    ordered[topic] = ([date], {num: answers[date]})

                answers[date][2].append("Ordered")

        n += 1
        if n == 366:
            break


assert len(answers) == 366
answers = dict(sorted(answers.items(), key=lambda p: sort_key(p[0])))
current = score()

# Category spread maximization
for _ in range(MIX):
    a, b = random.choices(list(answers.keys()), k=2)
    swap(a, b)
    if (future := score()) < current:
        swap(a, b)
    else:
        current = future


# Ordered clue sorting
for topic in ordered:
    for index, entry in enumerate(sorted(ordered[topic][0], key=sort_key)):
        answers[entry] = ordered[topic][1][index]


# Final write
answers = dict(sorted(((answer, tup[:2]) for answer, tup in answers.items()), key=lambda p: sort_key(p[0])))
with open("data/answers.js", "w+") as file:
    string = json.dumps(answers).replace("'", "\\'")
    file.write(f"answers = JSON.parse('{string}')")
