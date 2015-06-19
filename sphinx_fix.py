import os


def replace(f):
    f_t=f+".tmp"
    file_f=open(f,"r")
    file_t=open(f_t,"w")
    for s in file_f:
        file_t.write(s.replace('_static','stylesheets'))
    file_t.close()
    file_f.close()
    os.system("mv "+f_t+" "+f)

files=os.listdir(".")
for f in files:
    if f.find("html")>=0:
        print f
        replace(f)
        