import os
import zipfile
import uuid
from collections import OrderedDict
from typing import Callable

from ens.console import echo
from ens.dumper import Dumper
from ens.models import Info, Catalog


tpl_mimetype = 'application/epub+zip'

tpl_container = '<?xml version="1.0" encoding="utf-8"?><container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0"><rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'

tpl_cover = '<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml"><head><title>Cover</title><link href="../stylesheet.css" rel="stylesheet" type="text/css"/></head><body><h1>{title}</h1><p class="author">—— {author}</p></body></html>'

tpl_chapter = '<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml"><head><title>{title}</title><link href="../stylesheet.css" rel="stylesheet" type="text/css"/></head><body><h3>{title}</h3>{content}</body></html>'

tpl_volume = '<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml"><head><title>{title}</title><link href="../stylesheet.css" rel="stylesheet" type="text/css"/></head><body><h2>{title}</h2></body></html>'

tpl_toc = '<?xml version="1.0" encoding="utf-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta content="{uid}" name="dtb:uid"/><meta content="-1" name="dtb:depth"/><meta content="0" name="dtb:totalPageCount"/><meta content="0" name="dtb:maxPageNumber"/></head><docTitle><text>{title}</text></docTitle><navMap>{nav}</navMap></ncx>'

tpl_content = '<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf"><dc:title>{title}</dc:title><dc:identifier id="BookID" opf:scheme="UUID">{uid}</dc:identifier><dc:author>{author}</dc:author><dc:subject>ens-dump</dc:subject><dc:language>zh-CN</dc:language><dc:creator>{author}</dc:creator></metadata><manifest><item href="stylesheet.css" id="styleshee" media-type="text/css"/><item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>{manifest}</manifest><spine toc="ncx">{spine}</spine><guide></guide></package>'

default_style = '''@namespace h "http://www.w3.org/1999/xhtml"; body {display: block; margin: 5pt; page-break-before: always; text-align: justify; } h1, h2, h3 {text-align: center; font-weight: bold; margin-bottom: 1em; margin-left: 0; margin-right: 0; margin-top: 1em; } p {margin-bottom: 1em; margin-left: 0; margin-right: 0; margin-top: 1em; } .author {text-align: right; font-weight: bold; }'''


class Volume(object):

    def __init__(self, vol_title):
        self.title = vol_title
        self.chaps_titles = []

    def __iter__(self):
        return iter(self.chaps_titles)

    def push(self, title):
        self.chaps_titles.append(title)


class EPUBDumper(Dumper):
    ext = '.epub'

    def dump(self, info: Info, catalog: Catalog, get_chap: Callable[[str], str], path: str):
        self.zip = zipfile.ZipFile(path, 'w')

        self.write('mimetype', tpl_mimetype)
        self.write('META-INF', 'container.xml', tpl_container)

        self.chapters = 1
        self.volumes = 1
        self.spine = []
        self.navmap = []
        self.manifest = OrderedDict()

        self.uid = uuid.uuid4() # 随机数uuid

        self.title = info.title
        self.author = info.author
        self.write('stylesheet.css', default_style)
        self.write('text', 'cover_page.xhtml',
            tpl_cover.format(title=info.title, author=info.author)
        )
        self.spine.append('cover')
        self.manifest['cover'] = 'cover_page.xhtml'

        for nav in catalog.nav_list():
            if nav.type == 'chap':
                cid = catalog.spine[nav.index].cid
                self.chap(nav.title, get_chap(cid))
            elif nav.type == 'vol':
                self.vol(nav.title)

        self.write_toc()
        self.write_content()
        self.zip.close()


    def write(self, *args):
        paths = args[:-1]
        data = args[-1]
        self.zip.writestr(os.path.join(*paths), data)


    def push_volume(self, title):
        self.navmap.append(Volume(title))


    def push_chapter(self, title):
        self.navmap[-1].push(title)


    def content_proc(self, content):
        lines = content.\
            replace('&', '&amp;').\
            replace('<', '&lt;').\
            replace('>', '&gt;').\
            replace('"', '&quot;').split('\n')

        return ''.join(
            '<p>{}</p>'.format(line) for line in lines
        )


    def chap(self, title, content):
        src_id = 'chap_{:0>4}'.format(self.chapters)
        src_name = 'chap_{:0>4}_page.xhtml'.format(self.chapters)
        self.chapters += 1

        self.write('text', src_name,
            tpl_chapter.format(
                title=title,
                content=self.content_proc(content)
            )
        )
        self.spine.append(src_id)
        self.manifest[src_id] = src_name
        self.push_chapter(title)


    def vol(self, title):
        src_id = 'vol_{:0>4}'.format(self.volumes)
        src_name = 'vol_{:0>4}_page.xhtml'.format(self.volumes)
        self.volumes += 1

        self.write('text', src_name, tpl_volume.format(title=title))
        self.spine.append(src_id)
        self.manifest[src_id] = src_name
        self.push_volume(title)


    def write_toc(self):
        nav = ''
        this_volume = 1
        this_chapter = 1
        order = 1

        nav += '<navPoint id="order_{order}" playOrder="{order}"><navLabel><text>{title}</text></navLabel><content src="text/cover_page.xhtml"/></navPoint>'.\
            format(order=order, title=self.title)
        order += 1

        for volume in self.navmap:

            nav += '<navPoint id="order_{order}" playOrder="{order}"><navLabel><text>{title}</text></navLabel><content src="text/vol_{num:0>4}_page.xhtml"/>'.\
                format(order=order, title=volume.title, num=this_volume)
            this_volume += 1
            order += 1

            for chap_title in volume:
                nav += '<navPoint id="order_{order}" playOrder="{order}"><navLabel><text>{title}</text></navLabel><content src="text/chap_{num:0>4}_page.xhtml"/></navPoint>'.\
                    format(order=order, title=chap_title, num=this_chapter)
                this_chapter += 1
                order += 1

            nav += '</navPoint>'

        self.write('toc.ncx',
            tpl_toc.format(title=self.title, nav=nav, uid=self.uid)
        )


    def write_content(self):
        spine = ''.join(
            '<itemref idref="{}"/>'.format(src_id)
            for src_id in self.spine
        )

        manifest = ''.join(
            '<item href="text/{}" id="{}" media-type="application/xhtml+xml"/>'.format(src_name, src_id)
            for src_id, src_name in self.manifest.items()
        )

        self.write('content.opf',
            tpl_content.format(
                title = self.title,
                author = self.author,
                spine = spine,
                manifest = manifest,
                uid = self.uid
            )
        )


export = EPUBDumper
