# -*- coding: utf-8 -*-
"""
    BobSwitch 
    ~~~~~~~~~~~~~~

    Online HTML5 version of the backpackers card game switch, also known as crazy eights 
    and a lot of different names.  This version follows the rules that I know.

    :copyright: (c) Copyright 2013 by Bob
    :license: BSD, see LICENSE for more details.
"""

from random import SystemRandom
from flask import Flask, render_template, session, request, \
        url_for, redirect, Response, jsonify


app = Flask(__name__)
app.config.from_pyfile('config.py')
    
random = SystemRandom()


@app.route('/', methods=['GET', 'POST'])
def pick_a_game():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
