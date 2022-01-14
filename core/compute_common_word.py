from collections import Counter
import sqlite3
import jieba
from tools import get_content_from_sql, cut_content_into_words


def find_most_freq_words(content_cut):
    counter = Counter(content_cut)
    ordered_freq_word = list(dict(sorted(counter.items(), key=lambda item: item[1], reverse=True)).keys())
    ordered_freq_word = list(filter(lambda s: len(s) > 1, ordered_freq_word))[:15]
    return ordered_freq_word


if __name__ == '__main__':
    common = [
        '然後',
        '不過',
        '但是',
        '時候',
        '因為'
    ]
    
    content_cut = cut_content_into_words(get_content_from_sql())
    common += find_most_freq_words(content_cut)
    common = list(set(common))
    
    with open('common_words.txt', 'w', encoding='UTF-8') as file:
        file.writelines(map(lambda s: s + '\n', common))