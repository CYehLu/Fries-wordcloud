import sqlite3
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from tools import get_content_from_sql, get_common_words, cut_content_into_words, plot_wordcloud


if __name__ == '__main__':
    content_cut = cut_content_into_words(get_content_from_sql())
    
    common_words = get_common_words()
    content_cut_filtered = list(filter(lambda s: s not in common_words, content_cut))
    
    plot_wordcloud(content_cut, './wordclouds/ALL.png')
    plot_wordcloud(content_cut_filtered, './wordclouds/ALL_filtered.png')
    
    