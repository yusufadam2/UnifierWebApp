from os.path import abspath


def ABS(root, path):
    return abspath(f'{root}/{path}')


def READ(fpath):
    with open(fpath) as f:
        return ''.join(f.readlines())


def WRITE(fpath, contents):
    with open(fpath, mode='w') as f:
        f.write(contents)


def has_extension(fpath, ext):
    return fpath.split('.')[-1] == ext


