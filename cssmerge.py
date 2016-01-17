import os, sys

__out = "../../flat/"

def cssmerge(fullpath, outfile):
    path, filename = os.path.split(os.path.normpath(fullpath))
    infile = file(os.path.join(path,filename), 'rU')
    skip = 0
    incurly = 0
    nr = 0
    for line in infile:
        nr += 1
        line = line.strip()

		#if line.count("{")>0:
		#	if incurly :
		#		print "ERROR: double curly @ "+fullpath+":"+`incurly`+"-"+`nr`
		#		sys.exit()
		#	else : incurly = nr

		#if line.count("}")>0:
		#	if incurly : incurly = 0
		#	else:
		#		print "ERROR: negative curly @ "+fullpath+":"+`nr`
		#		sys.exit()
    
        if line.startswith("@import"):
            monkey = line[line.find('"')+1:line.rfind('"')]
            outfile.write("/*"+monkey+"*/\n")
            cssmerge(os.path.join(path,monkey), outfile)
        elif line.endswith("}"):
            outfile.write(line+"\n\n")
        elif line != "":
            outfile.write(line+"\n")
    infile.close()

def cssm(cssfile="/"):
    if os.path.exists(__out) is False:
        os.mkdir(__out)

    for line in file('stylelist','rU').readlines():
        if not line.startswith('#') and line.find(cssfile) > 0:
            path,name = line.rstrip('\n').rsplit('/',1)
            dirname   = path.lstrip('./').replace('/','-')
            if 'aniidiot' in dirname or 'cdb' in dirname:
                crap, dirname = path.rsplit('/', 1)
            out = __out+dirname
            if os.path.exists(out) is False:
                os.mkdir(out)
            try:
                cssmerge(line.rstrip('\n'), file(out + '/' + dirname + '.css', 'w'))
            except Exception as e:
                print out + '/' + path.lstrip('./').replace('/','-') + '.css'
                print e

if __name__ == "__main__":
    if len(sys.argv) == 2:
        cssm(sys.argv[1])
    else:
        cssm()
    print "done"
