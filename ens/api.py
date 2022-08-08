from flask import Flask
from flask import request, jsonify, render_template, redirect

from ens.paths import FLASK_PATH
from ens.models import *
from ens.local import *
from ens.exceptions import *


def get_local(remote, nid):
    novel = Novel((remote, nid))
    try:
        return LocalStorage(novel)
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
    prev = spine[pos-1] if pos != 0 else None
    next = spine[pos+1] if pos != len(spine)-1 else None

    try:
        content = local.get_chap(cid)
    except ChapMissing:
        content = '[内容丢失]'

    return render_template('chap.html',
        ntitle = local.info.title,
        title = local.get_title(cid),
        content = content,
        path = f'{remote}/{nid}',
        prev = f'/chap/{remote}/{nid}/{prev}' if prev else '',
        next = f'/chap/{remote}/{nid}/{next}' if next else ''
    )