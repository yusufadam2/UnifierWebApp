#!/usr/bin/env python3

import os
import sys

from datetime import datetime
from utils import ABS, has_extension, READ, WRITE

PLACEHOLDERS = {
    'TITLE': 'TITLE',
    'CONTENT': 'PLACEHOLDER',
    'LIST_ITEM': 'LIST_ITEM',
}

def template(layout_fpath, placeholder_map, src_fpath, dst_fpath):
    layout = READ(layout_fpath)
    src = READ(src_fpath)

    out = layout.replace(PLACEHOLDERS['CONTENT'], src)

    for key, value in placeholder_map.items():
        out = out.replace(PLACEHOLDERS[key], str(value))

    WRITE(dst_fpath, out)


def template_list(src_fpath, item_src_fpaths, dst_fpath):
    src = READ(src_fpath)
    ITEM_PLACEHOLDER = PLACEHOLDERS['LIST_ITEM']

    for item_src_fpath in item_src_fpaths:
        item_src = READ(item_src_fpath)

        src = src.replace(
            ITEM_PLACEHOLDER, item_src + f'\n{ITEM_PLACEHOLDER}')

    out = src.replace(ITEM_PLACEHOLDER, '')

    WRITE(dst_fpath, out)


if __name__ == '__main__':
    args, expected = sys.argv, 5

    if '-h' in args or len(args) != expected:
        print(f'Usage: {__file__} <html_dir> <layout_dir> <tmp_dir> <out_dir>')
        print(f'\t-h : Display this help information')

    html_dir, layout_dir, tmp_dir, out_dir = (*args[1:expected],)

    page_layout = ABS(layout_dir, '_Layout.html')

    ## template all html pages
    for page in os.listdir(html_dir):
        page_fpath = os.path.join(html_dir, page)
        if os.path.isfile(page_fpath) and has_extension(page, 'html'):
            ext_len = len('.html')  ## for stripping the file extension from the title
            normalised_title = f'{page[0].upper()}{page[1:-ext_len]}'
            template(page_layout, {'TITLE': normalised_title},
                    ABS(html_dir, page),
                    ABS(out_dir, page))

