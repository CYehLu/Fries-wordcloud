from collections import Counter
import sqlite3
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud


PUNC = """!()-[]{};:'"\, <>./?@#$%^&*_~！？，。；：、（）「」【】《》〈〉『』"""

def get_common_words():
    """
    Return common words (return type: List[str])
    """
    with open('common_words.txt', encoding='utf-8') as file:
        common_words = list(map(lambda s: s.strip(), file.readlines()))
    return common_words

def get_all_userid():
    """
    Return all user id (return type: List[str])
    """
    with open('all_userid.txt') as file:
        all_userid = list(map(lambda s: s.strip(), file.readlines()))
    return all_userid

def get_content_from_sql():
    """
    Return all contents
    """
    conn = sqlite3.connect('./fries.sqlite')
    c = conn.cursor()
    c.execute('SELECT content FROM fries WHERE content IS NOT NULL;')
    conn.commit()
    content = c.fetchall()
    content = list(map(lambda s: s[0].strip(), content))
    conn.close()
    return content

def get_content_of_user_from_sql(userid):
    """
    Return all contents of userid
    input type: str
    """
    conn = sqlite3.connect('./fries.sqlite')
    c = conn.cursor()
    c.execute(f'SELECT content FROM fries WHERE user_id = "{userid}" AND content IS NOT NULL;')
    conn.commit()
    content = c.fetchall()
    content = list(map(lambda s: s[0].strip(), content))
    conn.close()
    return content

def cut_content_into_words(content):
    """
    Cut content by jieba
    input type: List[str], output type: List[str]
    """
    long_str = ' '.join(content)
    content_cut = list(filter(lambda s: s.strip() not in PUNC, jieba.cut(long_str)))
    return content_cut

def plot_wordcloud(content_cut, filename):
    """
    Given the cut content, plot and save the wordcloud.
    input type: List[str], str
    """
    plt.figure()
    plt.imshow(WordCloud(font_path='ext/jf-openhuninn-1.1/jf-openhuninn-1.1.ttf').generate(' '.join(content_cut)))
    plt.axis('off')
    plt.savefig(filename, bbox_inches='tight')
    
def plot_wordcloud_by_userid(userid, filter_other_id=True):
    content = get_content_of_user_from_sql(userid)
    
    if len(content) == 0:
        raise ValueError(f"No content of {userid}")
        
    content_cut = cut_content_into_words(content)
    
    # filter out common words
    common_words = get_common_words()
    content_cut_filtered = list(filter(lambda s: s not in common_words, content_cut))
    
    # filter out others ID
    if filter_other_id:
        all_userid = get_all_userid()
        content_cut_filtered = list(filter(lambda s: s not in all_userid, content_cut_filtered))
    
    plot_wordcloud(content_cut, f'./wordclouds/{userid}.png')
    plot_wordcloud(content_cut_filtered, f'./wordclouds/{userid}_filtered.png')