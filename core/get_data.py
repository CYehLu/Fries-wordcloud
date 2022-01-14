import time
import random
import re
import requests
import sqlite3
from bs4 import BeautifulSoup


class SectionsParser:
    def __init__(self, sections):
        self.sections = sections
        
    def parse(self):
        res = []
        for section in sections[1:-3]:
            status = self._check_post_status(section)
            if status == 'normal':
                res += self._parse_post(section)
            elif status == 'delete':
                res += self._parse_delete_post(section)
            elif status == 'fold':
                res += self._parse_fold_post(section)
                
        return res
    
    def _check_post_status(self, section):
        hint = section.find('div', class_='hint')
        if hint is None:
            return 'normal'
        elif '折疊' in hint.text:
            return 'fold'
        else:
            return 'delete'
        
    def _parse_delete_post(self, section):
        floor = section.find('div', class_='floor').text
        hint_text = section.find('div', class_='hint').text
        
        try:
            # 自刪的會留下ID, 被系統刪除的不會
            userid = re.findall('\(.+\)', hint_text)[0][1:-1]
        except IndexError:
            userid = None
            
        return [[floor, None, None, None, userid, None, None, None, None]]
    
    def _parse_fold_post(self, section):
        # I have no idea how to deal with this situation...
        floor = section.find('div', class_='floor').text
        hint_text = section.find('div', class_='hint').text
        userid = re.findall('.*【(.+)的文章已折疊】.*', hint_text)[0].strip()
        gp = re.findall('.+】([0-9]+).*推.+', hint_text)[0]
        bp = re.findall('.+．([0-9]+).*噓.*', hint_text)[0]
        return [[floor, None, None, None, userid, gp, bp, None, None]]
        
    def _parse_post(self, section):
        # post header
        floor = section.find('a', class_='floor tippy-gpbp').text
        username = section.find('a', class_='username').text
        userid = section.find('a', class_='userid').text
        gp = section.find('span', class_='postgp').text
        bp = section.find('span', class_='postbp').text
        time = section.find('a', class_='edittime tippy-post-info').text

        # post body
        content = section.find('div', class_='c-article__content').text

        # post replies
        if section.find('a', class_='more-reply'):
            replies = self._parse_more_replies(section)
        else:
            replies = self._parse_replies(section)
        
        # return results
        res = []
        res.append([floor, None, None, username, userid, gp, bp, time, content]) 
        for reply in replies:
            res.append([None, floor] + reply)
            
        return res           
        
    def _parse_replies(self, section):
        reply_items = section.find_all('div', class_='c-reply__item')
        
        replies = []
        
        for i, reply_item in enumerate(reply_items):
            reply_username = reply_item.find('a', class_='reply-content__user').text
            reply_userid = reply_item.find('a', class_='reply-content__user')['href'].split('/')[-1]
            reply_content = reply_item.find('article', class_='reply-content__article c-article').text
            reply_time = reply_item.find('div', class_='edittime').text
            reply_gp = reply_item.find('a', class_='gp-count')['data-gp']
            reply_bp = reply_item.find('a', class_='bp-count')['data-bp']
            
            replies.append([
                i,
                reply_username,
                reply_userid,
                reply_gp,
                reply_bp,
                reply_time,
                reply_content
            ])
            
        return replies
    
    def _parse_more_replies(self, section):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        url = self._get_more_reply_url(section)
        resp = requests.get(url, headers=headers)
        
        res = []
        i = 0
        
        for line in resp.content.decode('unicode_escape').split('\n'):
            if line.startswith('<a class="reply-content__user"'):
                # for example
                # line = '<a class="reply-content__user" href="\/\/home.gamer.com.tw\/BAHAMUT000" target="_blank">薯條控<\/a>'
                reply_userid = line.split()[2].split('/')[-1][:-1]
                reply_username = line.split('"_blank">')[-1].split('<')[0]
                
                res.append(i)
                res.append(reply_username)
                res.append(reply_userid)
                i += 1

            elif line.startswith('<article class="reply-content__article c-article "'):
                # for example
                # line = '<article class="reply-content__article c-article "><span>個人認為差有點多...<\\/span><\\/article>'
                reply_content = line.split('<span>')[-1].split('<\\/span>')[0]
                res.append(reply_content)

            elif line.startswith('<div class="edittime"'):
                # for example
                # line = '<div class="edittime" title="留言時間 2016-01-20 13:06:35">2016-01-20 13:06:35<\\/div>'
                reply_time = line.split('>')[1].split('<')[0]
                res.append(reply_time)

            elif line.startswith('<a data-gp='):
                # for example
                # line = '<a data-gp=0 href="javascript:;" class="gp-count"><\\/a>',
                reply_gp = line.split()[1].split('=')[1]
                res.append(reply_gp)

            elif line.startswith('<a data-bp='):
                # for example
                # line = '<a data-bp=0 href="javascript:;" class="gp-count"><\\/a>',
                reply_bp = line.split()[1].split('=')[1]
                res.append(reply_bp)
                
        # "reshape" res from 1d to 2d
        final_res = []
        for i in range(len(res)//7):
            one_reply = res[7*i:7*i+7]
            final_res.append([
                one_reply[0],   # index 
                one_reply[1],   # user name
                one_reply[2],   # user id
                one_reply[5],   # gp
                one_reply[6],   # bp
                one_reply[4],   # time
                one_reply[3]    # content
            ])
          
        return final_res
        
    def _get_more_reply_url(self, section):
        snB = section.find('a', class_='more-reply')['id'].split('_')[-1]
        return f'https://forum.gamer.com.tw/ajax/moreCommend.php?bsn=60076&snB={snB}&returnHtml=1'
    
    
if __name__ == '__main__':
    page_start = 1
    page_end = 1795
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    
    for page in range(page_start, page_end+1):
        print(f"page : {page} ... ", end='')
        
        # send a request and parse the response
        url = f'https://forum.gamer.com.tw/C.php?page={page}&bsn=60076&snA=3146926'
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text)
        
        sections = soup.find_all('section', class_='c-section')
        res = SectionsParser(sections).parse()
        
        # store in DB
        conn = sqlite3.connect('fries.sqlite')
        c = conn.cursor()
        c.executemany(
            'INSERT INTO fries (floor, parent_floor, reply_floor, user_name, user_id, gp, bp, time, content) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
            res
        )
        conn.commit()
        conn.close()
        
        print('[Done]')
        time.sleep(3*random.random())