import os
import requests
import zipfile

if __name__ == '__main__':
    print('Download font .ttf file...')
    
    url = 'https://github.com/justfont/open-huninn-font/releases/download/v1.1/jf-openhuninn-1.1.zip'
    resp = requests.get(url)
    
    with open('ext/jf-openhuninn-1.1.zip', 'wb') as f:
        f.write(resp.content)

    with zipfile.ZipFile('ext/jf-openhuninn-1.1.zip', 'r') as zipf:
        zipf.extractall('ext/')
    
    print('[done]')