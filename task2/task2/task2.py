import string

from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

import requests


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException as e:
        print(f"Помилка: Не вдалося отримати вхідний текст.: {e}")
        return None


# Функція для видалення знаків пунктуації
def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


# Виконання MapReduce
def map_reduce(text):
    # Видалення знаків пунктуації
    text = remove_punctuation(text)
    words = text.split()

    # В порівнянні з кодом із теорії, нам потрібно порахувати кількість всіх слів у тексті, а не окремих бажаних.
    # Отже words - це список зі всіх слів.

    # Паралельний Мапінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Паралельна Редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def visualize_top_words(words: dict, number_of_words: int):
    # First of all, let's sort a given dictionary, in case if it's not
    sorted_dict = {k: v for k, v in sorted(words.items(), key=lambda item: item[1], reverse=True)}

    top_words_dict = {}

    for i, key in enumerate(sorted_dict):
        if i < number_of_words:
            top_words_dict[key] = sorted_dict[key]
    
    # Time ti visualize
    fig, ax = plt.subplots()

    ax.barh(top_words_dict.keys(), top_words_dict.values())
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Amount of words')
    ax.set_title(f'Top {number_of_words} words in "1984"')

    # Empirically set an autosizing of the figure. Works fine for number of words up to 50
    fig.set_size_inches(6, number_of_words*0.1+3)

    plt.show()


if __name__ == '__main__':
    # Вхідний текст для обробки
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    text = get_text(url)
    
    NUMBER_OF_WORDS = 10        # Використовується для виводу топ-10 найчастіше вживаних слів у тексті. Змінити на 'х' для топ-х.
    
    if text:
        # Виконання MapReduce на вхідному тексті
        result = map_reduce(text)

        # print("Результат підрахунку слів:", result)
    else:
        print("MapReduce не виконався, пошукайте помилку в коді.")
        
    visualize_top_words(result, NUMBER_OF_WORDS)
