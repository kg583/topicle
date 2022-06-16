import unidecode

from randomizer import answers


allowed = set()
MIN = 119

# Wikipedia words
with open("data/enwiki-20210820-words-frequency.txt", encoding='utf-8') as file:
    for line in file.readlines():
        word, count = line.split()
        if int(count) >= MIN:
            word = unidecode.unidecode(word)
            if word.isalpha() and len(word) == 5:
                allowed.add(word.upper())


# Wordle words
with open("data/words.txt") as file:
    for line in file.readlines():
        allowed.add(line.strip().upper())


# All clue words
for _, entry in answers.items():
    for word in entry[1]:
        allowed.add(word.upper())


allowed = sorted(allowed)
with open("data/allowed.js", "w+") as file:
    file.write(f"allowed = '{' '.join(allowed)}'.split(' ')")
