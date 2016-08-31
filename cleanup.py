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
        tmp              = []
        content          = []
        openbrackets     = 0
        properties       = False
        mediaquery       = False
        forceNormalBreak = False
        for line in file(filepath):
            line = self._cleanup_string(line.decode('utf8'))
            hasContent = True if len(content) > 0 else False
            
            if line == u'':
                continue
            elif line.startswith((u'@media', u'@supports')):
                mediaquery = True
                openbrackets += 1
                content.append(u'%s%s' %(u'\n\n'if hasContent and not forceNormalBreak else '\n' if forceNormalBreak and hasContent else u'', line, ))
                forceNormalBreak = True
            elif line.startswith(u'/*'):
                #comment
                forceNormalBreak = True
                content.append(u'%s%s%s%s%s%s' %(u'\n\n'if hasContent and not forceNormalBreak else '\n' if forceNormalBreak and hasContent else u'', u'\t' if mediaquery else u'', '' if properties or not hasContent else u'\n', '\t' if mediaquery else u'', '\t' if properties else u'', line))
            elif line.startswith(u'{'):
                #start of properties block
                properties = True
                openbrackets += 1
                content.append(u'%s%s {' %(u'\n\n'if hasContent and not forceNormalBreak else '\n' if forceNormalBreak and hasContent else u'', self._build_rules(tmp), ))
                tmp = []
            elif line.startswith(u'}'):
                #segment ended
                forceNormalBreak = False
                properties = False
                openbrackets -= 1
                if openbrackets == 0 and mediaquery:
                    mediaquery = False

                content.append(u'%s%s%s' %(u'\n' if hasContent else '', u'\t' if mediaquery else u'', line, ))
            elif line.endswith(u'{'):
                #last rule in segment
                properties = True
                openbrackets += 1
                line = line.rstrip(u'{').strip()
                if ',' in line:
                    for bit in line.split(','):
                        tmp.append(u'%s%s' %(u'\t' if mediaquery else u'', bit.strip()))
                else:
                    tmp.append(u'%s%s' %(u'\t' if mediaquery else u'', line))
                content.append(u'%s%s {' %(u'\n\n'if hasContent and not forceNormalBreak else '\n' if forceNormalBreak and hasContent else u'', self._build_rules(tmp), ))
                forceNormalBreak = False
                tmp = []
            elif properties:
                #all dem properties
                content.append(u'%s\t%s%s' %(u'\n' if hasContent else '', u'\t' if mediaquery else u'', line.replace(':', ': ').replace('  ', ' ')))
            elif line.startswith(u'@import'):
                content.append(u'%s%s%s' %(u'\n' if hasContent else '', u'\t' if mediaquery else u'', line, ))
            else:
                #rules
                if line.endswith(u','):
                    line = line.rstrip(u',')

                if ',' in line:
                    for bit in line.split(','):
                        tmp.append(u'%s%s' %(u'\t' if mediaquery else u'', bit))
                else:
                    tmp.append(u'%s%s' %(u'\t' if mediaquery else u'', line))

            #print u'----------------'
            #print line
            #print openbrackets
            #print tmp
            #print hasContent, forceNormalBreak

        file(filepath, 'w').write(u''.join(content).encode('utf8'))
        #print u''.join(content)

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
                    self._process_file(os.path.join(root, filename))

if __name__ == '__main__':
    cleaner(os.getcwd())
