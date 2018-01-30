# coding=utf-8
# @Time : 2018/1/15 18:07
# @Author : 李飞
from collections import Iterable

import requests
import random
import math
import binascii
import base64
import json
import os
from Crypto.Cipher import AES
import threading
import time
import re
from requests.exceptions import MissingSchema


class Wangyiyun(object):
    def __init__(self, song_ids, type):
        if type != 'playlist' and type != 'song':
            raise BaseException('请传入正确的类型')
        if type == 'song':
            if not isinstance(song_ids, Iterable):
                raise BaseException('请传入一个id列表集合')
            self.song_ids = song_ids
        else:
            if not isinstance(song_ids, str) and not isinstance(song_ids, int):
                raise BaseException('请传入正确的id')
            self.song_ids = song_ids
        self.type = type
        self.sec = Secrect()
        self.session = requests.session()
        self.header = {
            'Connection': 'close',
            'Host': 'music.163.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }

    def download(self):
        if self.type == 'playlist':
            self.getidlist(playlist_id=self.song_ids)

        print('ready----->GO')
        for id in self.song_ids:
            song_data = {}
            song_data['id'] = id
            song_data['c'] = "[{\"id\": %s}]" % id
            song_data = self.sec.get_secret_data(**song_data)
            response = self.session.post(url='http://music.163.com/weapi/v3/song/detail?csrf_token=',
                                         data=song_data,
                                         cookies={}, headers=self.header)
            result = json.loads(response.text)

            t = threading.Thread(target=self.parser_url, args=result['songs'])
            t.start()

    def getidlist(self, playlist_id):
        header = {
            'Connection': 'close',
            'Host': 'music.163.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }
        url = 'http://music.163.com/playlist?id=%s' % playlist_id
        result = requests.get(url, headers=header)
        regx = r'href="/song\?id=(\d+)"'
        ids = re.findall(regx, result.text, re.S | re.M | re.DOTALL)
        self.song_ids = list(set(ids))
        if len(self.song_ids) == 0:
            raise BaseException('歌单数据获取失败...')
        else:
            print('歌单数据加载完成...')

    def parser_url(self, *args):
        postdata = {
            'ids': "[%s]" % args[0]['id'],
            'br': str(args[0]['l']['br'])
        }
        postdata = self.sec.get_secret_data(**postdata)
        name = args[0]['name'] + '-' + args[0]['ar'][0]['name']
        response = self.session.post(url='http://music.163.com/weapi/song/enhance/player/url?csrf_token=',
                                     data=postdata, cookies=None, headers=self.header)
        try:
            url = json.loads(response.text)['data'][0]['url']
            print('start download %s' % name)
            r = self.session.get(url=url, stream=True)
            f = open("%s.mp3" % name, "wb")
            for chunk in r.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
            f.close()
            print('download OK %s ' % name)
        except KeyError:
            print('%s parser failed' % name)
        except MissingSchema:
            print('请确保网易云搜索----%s-----能正常播放' % name)


class Secrect(object):
    def __init__(self):
        self.nonce = '0CoJUm6Qyw8W8jud'
        self.pubKey = '010001'
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615' \
                       'bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ec' \
                       'bda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e8' \
                       '2047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'

    def create_random_secrekey(self, size):
        b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        c = ''
        for i in range(size):
            e = random.random() * len(b)
            e = math.floor(e)
            c += b[e]
        return c

    def aes_encrypt(self, text, sec_key):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(sec_key.encode('utf-8'), 2, '0102030405060708'.encode('utf-8'))
        ciphertext = encryptor.encrypt(text.encode('utf-8'))
        ciphertext = base64.b64encode(ciphertext)
        return ciphertext.decode('utf-8')

    def rsa_encrypt(self, text, pubKey, modulus):
        text = text[::-1]
        rs = int(binascii.hexlify(text.encode('utf-8')), 16) ** int(pubKey, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)

    def get_secret_data(self, **kwargs):
        kw = {

        }
        for x in kwargs:
            kw[x] = kwargs[x]
        jsons = json.dumps(kw)
        secKey = self.create_random_secrekey(16)
        encText = self.aes_encrypt(self.aes_encrypt(jsons, self.nonce), secKey)
        encSecKey = self.rsa_encrypt(secKey, self.pubKey, self.modulus)
        result = {
            'params': encText,
            'encSecKey': encSecKey
        }
        return result


if __name__ == '__main__':
    # song_ids = ['452997509']
    """
    歌单参数为    歌单id    'playlist'
    歌曲参数为    歌曲id集合[]   'song'   type 只能为这两个值 
    """
    try:
        song_ids = ['525239736', '523251118', ]
        wangyiyun = Wangyiyun(song_ids=song_ids, type='song')
        wangyiyun.download()
    except BaseException as e:
        print(e)
