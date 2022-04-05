from flask import Flask
from flask import request, jsonify, render_template, redirect
from functools import lru_cache

from ens.paths import FLASK_PATH
from ens.typing import *
from ens.local import *
from ens.exceptions import *


def get_local(remote, nid):
    code = Code((remote, nid))
    try:
        return Local(code)
    except LocalNotFound:
        return None


api = Flask('api', root_path=FLASK_PATH)


@api.post('/search')
def search():
    shelf = get_local_shelf()
    
    if request.data:
        rules = request.json
        filter = ShelfFilter(
            [FilterRule(i) for i in rules]
        )
        shelf.apply_filter(filter)

    return jsonify(shelf)


@api.get('/')
def root():
    return redirect('/shelf')


@api.get('/shelf')
def view():
    return render_template('shelf.html')


@api.get('/novel/<remote>/<nid>')
def novel(remote, nid):
    local = get_local(remote, nid)
    
    return render_template('novel.html',
        info = local.info,
        nav = local.nav
    )


@api.get('/chap/<remote>/<nid>/<cid>')
def chap(remote, nid, cid):
    local = get_local(remote, nid)

    return render_template('chap.html',
        title = local.get_title(cid),
        content = local.get_chap(cid)
    )
