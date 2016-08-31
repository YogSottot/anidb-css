import os

class cleaner(object):
    REORDER = False
    DRYRUN  = True
    DEBUG   = True

    def __init__(self, path):
        self._search_css_files(path)

    def _cleanup_string(self, string):
        string = string.replace(u'\t', u' ').replace(u'*.', u'.')
        while u'  ' in string:
            string = string.replace(u'  ', u' ')

        return string.strip()

    def _process_file(self, filepath):
        tmp              = []
        content          = []
        openbrackets     = 0
        linecnt          = 0
        prevLine         = ''
        properties       = False
        mediaquery       = False
        forceNormalBreak = False
        multiLineComment = False
        for line in file(filepath):
            linecnt += 1
            line = line.decode('utf8').replace(u'\n', u'')
            hasContent = True if len(content) > 0 else False

            if line == u'':
                continue
            elif multiLineComment or line.strip().startswith(u'/*'):
                #comment
                if line.endswith(u'*/'):
                    if multiLineComment:
                        line += u'\n'

                    multiLineComment = False
                    forceNormalBreak = True
                else:
                    multiLineComment = True

                if line.strip().startswith(u'/*'):
                    line = self._cleanup_string(line)
                    content.append(u'%s%s%s%s%s' %(
                            u'\n' if hasContent else u'',
                            u'\n' if hasContent and not properties and not prevLine.startswith((u'@media', u'@supports')) else u'',
                            u'\t' if mediaquery else u'',
                            u'\t' if properties else u'',
                            line
                        )
                    )
                else:
                    content.append(u'\n%s' %(line))

                prevLine = self._cleanup_string(line)
                continue

            line = self._cleanup_string(line)
            if line.startswith((u'@media', u'@supports')):
                mediaquery = True
                openbrackets += 1
                content.append(u'%s%s' %(
                        u'\n\n'if hasContent and not forceNormalBreak else '\n' if forceNormalBreak and hasContent else u'',
                        line
                    )
                )
                forceNormalBreak = True
            elif line.startswith(u'{'):
                #start of properties block
                properties = True
                openbrackets += 1
                content.append(u'%s%s {' %(
                        u'\n\n' if hasContent and not forceNormalBreak else '\n' if forceNormalBreak and hasContent else u'',
                        self._build_rules(tmp)
                    )
                )
                tmp = []
            elif line.startswith(u'}'):
                #segment ended
                openbrackets -= 1
                if openbrackets == 0 and mediaquery:
                    mediaquery = False

                content.append(u'%s%s%s' %(
                        u'\n' if hasContent and (properties or mediaquery or (not prevLine.endswith(u'*/') and not mediaquery)) else '',
                        u'\t' if mediaquery else u'',
                        line
                    )
                )

                forceNormalBreak = False
                properties       = False
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

                content.append(u'%s%s {' %(
                        u'\n\n' if hasContent and not forceNormalBreak else '\n' if forceNormalBreak and hasContent else u'',
                        self._build_rules(tmp)
                    )
                )
                forceNormalBreak = False
                tmp = []
            elif properties:
                #all dem properties
                if (openbrackets == 0) or (openbrackets == 1 and mediaquery):
                    print "ERROR: missing ; or right bracket in file %s line %s" %(filepath, linecnt)
                    break

                content.append(u'%s\t%s%s' %(
                        u'\n' if hasContent else '',
                        u'\t' if mediaquery else u'',
                        line.replace(':', ': ').replace('  ', ' ')
                    )
                )
            elif line.startswith((u'@import', u'@charset')):
                content.append(u'%s%s%s' %(
                        u'\n' if hasContent else '', u'\t' if mediaquery else u'',
                        line
                    )
                )
            elif u'{' in line and line.endswith(u'}'):
                #oneliner
                rule, property = line.rstrip('}').split('{', 1)
                content.append(u'%s%s%s {\n\t%s%s\n%s}' %(
                        u'\n\n' if hasContent and not forceNormalBreak else '\n' if forceNormalBreak and hasContent else u'',
                        u'\t' if mediaquery else u'',
                        rule.strip(),
                        u'\t' if mediaquery else u'',
                        property.strip(),
                        u'\t' if mediaquery else u''
                    )
                )

                forceNormalBreak = False
            else:
                #rules
                if line.endswith(u';'):
                    #WAT? -> property
                    print "ERROR: expected rule, got property in file %s line %s" %(filepath, linecnt)
                    break

                if line.endswith(u','):
                    line = line.rstrip(u',')

                if ',' in line:
                    for bit in line.split(','):
                        tmp.append(u'%s%s' %(u'\t' if mediaquery else u'', bit))
                else:
                    tmp.append(u'%s%s' %(u'\t' if mediaquery else u'', line))

            prevLine = line

        content = u''.join(content).rstrip('\n')
        if not self.DRYRUN:
            if self.DEBUG:
                print content
            else:
                file(filepath, 'w').write(content.encode('utf8'))
        elif self.DEBUG:
            file(filepath + '.new', 'w').write(content.encode('utf8'))

    def _build_rules(self, rules):
        if self.REORDER:
            return u',\n'.join(sorted(rules, cmp=self._cmp_func))
        else:
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
