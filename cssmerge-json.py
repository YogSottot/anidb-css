'''
   munches several css files which are combined by @import sections into 1 css master file
   and copies the endresult into a specified folder
   furthermore creates a xml file which stays in the original folder and overwrites the existing one.
'''

import os, copy, datetime, sys, shutil, json

_out        = "../flat/"
_extensions = ('.jpg', '.jpeg', '.gif', '.png','.css')
_cssfolder  = []
_stylelist  = []

def cssmerge(fullpath, outfile):
    path, filename = os.path.split(os.path.normpath(fullpath))
    infile = file(os.path.join(path,filename), 'rU')
    skip = 0
    incurly = 0
    nr = 0
    for line in infile:
        nr += 1
        line = line.strip()

        if line.startswith("@import") and 'url(' not in line:
            monkey = line[line.find('"')+1:line.rfind('"')]
            outfile.write("/*"+monkey+"*/\n")
            cssmerge(os.path.join(path,monkey), outfile)
        elif line.endswith("}"):
            outfile.write(line+"\n\n")
        elif line != "":
            outfile.write(line+"\n")
    infile.close()

def cssm(cssfile="/"):
    if os.path.exists(_out) is False:
        os.mkdir(_out)

    for line in file('stylelist','rU'):
        if not line.startswith('#') and line.find(cssfile) > 0:
            path,name = line.rstrip('\n').rsplit('/',1)
            dirname   = path.lstrip('./').replace('/','-')
            if 'aniidiot' in dirname or 'cdb' in dirname:
                crap, dirname = path.rsplit('/', 1)
            out = _out + dirname
            add_to_stylelist(unicode(dirname),path)
            if os.path.exists(out) is False:
                os.makedirs(out)
            try:
                cssmerge(line.rstrip('\n'), file(out + '/' + dirname + '.css.new', 'w'))
            except Exception as e:
                print out + '/' + dirname + '.css.new'
                print e

            shutil.move(out + '/' + dirname + '.css.new', out + '/' + dirname + '.css')
            _cssfolder.append(path)

    file(_out + '/stylelist.json', 'w').write(json.dumps(_stylelist))

def add_to_stylelist(newstyle, path):
    svn      = {'day':18,'month':5,'year':2007} #date of the svn start. less bollocks now
    new      = {'id': newstyle, 'status': u'', 'description': u'', 'creator': u'', 'update': u'', 'title': u'', 'screenshot': u'', 'thumbnail': u''}
    descpath = path + '/' + 'description'
    if os.path.exists(descpath):
        last_key = None
        for line in file(descpath, 'r'):
            line = line.rstrip('\n')
            if line.find(':') >0:
                key, val = line.split(':', 1)
                key = key.lower()
                new[key] = unicode(val.strip())
                last_key = key
            elif new[last_key] == '':
                new[last_key] = line
            else:
                new[last_key] += '\n' + line

    for elem in ('thumbnail', 'screenshot'):
        if os.path.exists(os.path.join(path,'images',elem+'.png')):
            new[elem] = unicode(newstyle + '/' + 'images' +'/' +elem+'.png')
        else:
            new[elem] = u'none'

    newest = 0
    for filename in os.listdir(path):
        if filename.endswith('.css'):
            mtime = os.path.getmtime(path + '/' + filename)
            if mtime >  newest:
                newest = mtime

    newfile = datetime.datetime.fromtimestamp(newest)

    if newfile.day >= svn['day'] and newfile.month >= svn['month'] and newfile.year >= svn['year']:
        new['update'] = unicode(newfile.strftime('%d.%m.%Y'))

    _stylelist.append(new)

if __name__ == "__main__":
    cssm()
    print "done"
