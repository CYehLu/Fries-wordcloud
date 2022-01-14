import os
from flask import Flask, render_template, send_file, redirect, request
from core.tools import plot_wordcloud_by_userid

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        if request.values['send'] == '提交':
            userid = request.values['userid']
            
            if check_picture_pool(userid):
                return send_file(f'core/wordclouds/{userid}_filtered.png')
            else:
                try:
                    plot_wordcloud_by_userid(userid)
                    return send_file(f'core/wordclouds/{userid}_filtered.png')
                except ValueError:
                    return render_template('error.html')
                except Except as e:
                    return e
            
    return render_template('home.html')

def check_picture_pool(userid):
    """
    Check if {userid}.png has already existed at wordclouds/
    """
    all_pngs = os.listdir('core/wordclouds/')
    return any(filter(lambda s: s == f'{userid}.png', all_pngs))
    
if __name__ == '__main__':
    app.debug = True
    app.run()