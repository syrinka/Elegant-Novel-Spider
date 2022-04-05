from flask import Flask
from flask import request, jsonify, render_template, redirect

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


@api.get('/')
def root():
    return redirect('/shelf')


@api.get('/shelf')
def shelf():
    return render_template('shelf.html', 
        shelf = get_local_shelf()
    )


@api.get('/novel/<remote>/<nid>')
def novel(remote, nid):
    local = get_local(remote, nid)
    
    return render_template('novel.html',
        info = local.info,
        nav = local.nav()
    )


@api.get('/chap/<remote>/<nid>/<cid>')
def chap(remote, nid, cid):
    local = get_local(remote, nid)

    spine = local.spine()
    pos = spine.index(cid)

    return render_template('chap.html',
        ntitle = local.info.title,
        title = local.get_title(cid),
        content = local.get_chap(cid),
        path = f'{remote}/{nid}',
        prev = spine[pos-1] if pos != 0 else '',
        next = spine[pos+1] if pos != len(spine)-1 else ''
    )
