import unidecode


allowed = []

with open("enwiki-20210820-words-frequency.txt", encoding='utf-8') as file:
    for line in file.readlines():
        word, count = line.split()
        if int(count) >= 275:
            word = unidecode.unidecode(word)
            if word.isalpha() and len(word) == 5:
                allowed.append(word.upper())


allowed = sorted(allowed)
with open("allowed.js", "w+") as file:
    file.write(f"allowed = '{' '.join(allowed)}'.split(' ')")
