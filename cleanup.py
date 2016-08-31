import os

class cleaner(object):
    def __init__(self, path):
        self._search_css_files(path)

    def _cleanup_string(self, string):
        string = string.replace(u'\t', u' ').replace(u'\n', u'').replace(u'*.', u'.')
        while u'  ' in string:
            string = string.replace(u'  ', u' ')

        return string.strip()

    def _process_file(self, filepath):
        tmp                = []
        content            = []
        openbrackets       = 0
        properties         = False
        mediaquery         = False
        forcesinglenewline = False
        for line in file(filepath):
            line = self._cleanup_string(line.decode('utf8'))
            if line == u'':
                continue
            elif line.startswith(u'@'):
                mediaquery = True
                openbrackets += 1
                content.append(u'%s%s' %(u'\n\n'if len(content) > 0 and not forcesinglenewline else '\n' if forcesinglenewline and len(content) > 0 else u'', line, ))
                forcesinglenewline = True
            elif line.startswith(u'/*'):
                #comment
                forcesinglenewline = True
                content.append(u'%s%s%s%s%s' %(u'\n\n'if len(content) > 0 and not forcesinglenewline else '\n' if forcesinglenewline and len(content) > 0 else u'', u'\t' if mediaquery else u'', '' if properties else u'\n', '\t' if properties else u'', line))
            elif line.startswith(u'{'):
                #start of properties block
                properties = True
                openbrackets += 1
                content.append(u'%s%s {' %(u'\n\n'if len(content) > 0 and not forcesinglenewline else '\n' if forcesinglenewline and len(content) > 0 else u'', self._build_rules(tmp), ))
                tmp = []
            elif line.startswith(u'}'):
                #segment ended
                forcesinglenewline = False
                properties = False
                openbrackets -= 1
                if openbrackets == 0 and mediaquery:
                    mediaquery = False

                content.append(u'%s%s%s' %(u'\n' if len(content) > 0 else '', u'\t' if mediaquery else u'', line, ))
            elif line.endswith(u'{'):
                #last rule in segment
                properties = True
                openbrackets += 1
                tmp.append(u'%s%s' %(u'\t' if mediaquery else u'', line.rstrip(u'{').strip()))
                content.append(u'%s%s {' %(u'\n\n'if len(content) > 0 and not forcesinglenewline else '\n' if forcesinglenewline and len(content) > 0 else u'', self._build_rules(tmp), ))
                forcesinglenewline = False
                tmp = []
            elif properties:
                #all dem properties
                content.append(u'%s\t%s%s' %(u'\n' if len(content) > 0 else '', u'\t' if mediaquery else u'', line.replace(':', ': ').replace('  ', ' ')))
            else:
                #rules
                if line.endswith(u','):
                    line = line.rstrip(u',')

                tmp.append(u'%s%s' %(u'\t' if mediaquery else u'', line))

            #print u'----------------'
            #print line
            #print openbrackets
            #print tmp

        new = u'%s.new' %(filepath, )
        file(new, 'w').write(u''.join(content).encode('utf8'))
        #print u''.join(content)
        return new

    def _build_rules(self, rules):
        #return u',\n'.join(sorted(rules, cmp=self._cmp_func))
        return u',\n'.join(rules)

    def _cmp_func(self, a, b):
        if a.startswith(u'#') and not b.startswith(u'#'):
            return 1
        elif not a.startswith(u'#') and b.startswith(u'#'):
            return -1
        elif a > b:
            return 1
        elif a < b:
            return -1
        else:
            return 0

    def _search_css_files(self, path):
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith(u'.css'):
                    old = os.path.join(root, filename)
                    new = self._process_file(old)

if __name__ == '__main__':
    cleaner(os.getcwd())
