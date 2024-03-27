import sqlite3

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://academia.gal/dicionario/-/termo/{}"


def retrieve(word):
    response = requests.get(BASE_URL.format(word))

    response.raise_for_status()

    content = response.content.decode("utf-8")

    return content


def write_response(content):
    # save the content to a file
    with open("response_single.html", "w") as file:
        file.write(content)


def read_response():
    with open("response_single.html", "r") as file:
        return file.read()


class DicionarioError(Exception):
    pass


class NoDefinitionsError(Exception):
    pass


def parse(content):
    soup = BeautifulSoup(content, "html.parser")

    try:
        dicionario = soup.find("span", class_="Lemma")
    except AttributeError:
        raise DicionarioError

    if dicionario is None:
        raise DicionarioError

    definitions = dicionario.find_all("span", class_="Sense")

    if len(definitions) == 0:
        raise NoDefinitionsError

    if len(definitions) == 1:
        definition = definitions[0].find("span", class_="Definition__Definition")
        if not definition:
            raise NoDefinitionsError

        return [definition.text]

    else:
        return parse_multiple_definitions(definitions)


def parse_multiple_definitions(definitions):
    last_number = 0
    text_definitions = []

    for definition in definitions:
        number = definition.find("span", class_="Sense__SenseNumber")
        if number is None:
            continue

        number = int(number.text)
        if number < last_number:
            continue

        last_number = number

        definition = definition.find("span", class_="Definition__Definition")
        text_definitions.append(definition.text)

    return text_definitions


def read_thesaurus():
    thesaurus = "wordlist.txt"

    with open(f"data/{thesaurus}") as file:
        words = file.readlines()

    words = [word.strip() for word in words]
    return words


def init_db():
    conn = sqlite3.connect("dicionario.db")
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS words (word TEXT UNIQUE)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS definitions (words_rowid INTEGER, definition TEXT, "
        "FOREIGN KEY (words_rowid) REFERENCES words(ROWID))"
    )

    return cursor, conn


def save_to_db(word, definitions, cursor, conn):
    print(f"Inserting word: {word}")
    cursor.execute("INSERT OR IGNORE INTO words VALUES (?)", (word,))
    res = cursor.execute("SELECT last_insert_rowid();")
    word_id = res.fetchone()[0]

    for definition in definitions:
        cursor.execute(
            "INSERT OR IGNORE INTO definitions VALUES (?, ?)", (word_id, definition)
        )

        conn.commit()


def compose_dictionary(word):
    content = retrieve(word)
    print("----")
    print(f"Parsing {word}")
    try:
        return parse(content)
    except DicionarioError:
        print(f"Dicionario error for word: {word}")
    except NoDefinitionsError:
        print(f"No definitions found for word: {word}")


if __name__ == "__main__":
    cursor, conn = init_db()

    words = read_thesaurus()
    for word in words:
        if not word:
            continue

        res = cursor.execute("SELECT word FROM words WHERE word=?", (word,))
        db_word = res.fetchone()
        if db_word:
            print(f"{word} already inserted")
            continue

        definitions = compose_dictionary(word)
        if definitions:
            save_to_db(word, definitions, cursor, conn)

    conn.close()
