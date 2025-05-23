
def read_html(locpath = str):
    f = open(locpath, 'r', encoding='utf-8')
    s = f.read()
    return s