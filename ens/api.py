from flask import Flask
from flask import request, render_template, redirect

from ens.paths import FLASK_PATH
from ens.models import *
from ens.local import *
from ens.exceptions import *


def get_local(remote, nid):
    novel = Novel(remote, nid)
    try:
        return LocalStorage(novel)
    except LocalNotFound:
        return None


def resolve_query(query: str) -> Union[Filter, None]:
    if query is None:
        return None
    rules = []
    pieces = query.split()
    for piece in pieces:
        try:
            rule = FilterRule(piece)
        except BadFilterRule:
            rule = FilterRule('title=' + piece)
        rules.append(rule)
    return Filter(rules)


api = Flask('api', root_path=FLASK_PATH)


@api.get('/')
def root():
    return redirect('/shelf')


@api.get('/shelf')
def shelf():
    query = request.args.get('query')
    filter = resolve_query(query)
    return render_template('shelf.html', 
        shelf = get_local_shelf(filter)
    )


@api.get('/novel/<remote>/<nid>')
def novel(remote, nid):
    local = get_local(remote, nid)
    
    return render_template('novel.html',
        info = local.info,
        nav = local.catalog.nav_list()
    )


@api.get('/chap/<remote>/<nid>/<int:index>')
def chap(remote, nid, index):
    local = get_local(remote, nid)

    spine = local.catalog.spine
    chap = spine[index]
    prev = index-1 if index != 0 else None
    next = index+1 if index != len(spine)-1 else None

    try:
        content = local.get_chap(chap.cid)
    except KeyError:
        content = '[内容丢失]'

    return render_template('chap.html',
        ntitle = local.info.title,
        title = chap.title,
        content = content,
        path = f'{remote}/{nid}',
        prev = f'/chap/{remote}/{nid}/{prev}' if prev else '',
        next = f'/chap/{remote}/{nid}/{next}' if next else ''
    )
