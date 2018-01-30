# coding=utf-8
# @Time : 2017/7/18 17:50
# @Author : 李飞
import base64
import json
import os
from Crypto.Cipher import AES

nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'
modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7 '

"""
function a(a) {
        var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
        for (d = 0; a > d; d += 1)e = Math.random() * b.length, e = Math.floor(e), c += b.charAt(e);
        return c
    }
"""
import random
import math
import binascii


def create_random_secrekey(size):
    b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    c = ''
    for i in range(size):
        e = random.random() * len(b)
        e = math.floor(e)
        c += b[e]
    return c


def aes_encrypt(text, sec_key):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(sec_key.encode('utf-8'), 2, '0102030405060708'.encode('utf-8'))
    ciphertext = encryptor.encrypt(text.encode('utf-8'))
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext.decode('utf-8')


def rsa_encrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(binascii.hexlify(text.encode('utf-8')), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def get_secret_data(**kwargs):
    kw = {

    }
    for x in kwargs:
        kw[x] = kwargs[x]
    jsons = json.dumps(kw)
    secKey = create_random_secrekey(16)
    encText = aes_encrypt(aes_encrypt(jsons, nonce), secKey)
    encSecKey = rsa_encrypt(secKey, pubKey, modulus)
    result = {
        'params': encText,
        'encSecKey': encSecKey
    }
    return result
