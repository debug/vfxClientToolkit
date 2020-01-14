#!/usr/bin/python

import MySQLdb as mysql
import sys
import re
import os
import time
import cgi
import json

import rvSession

def hasCube(seq, shot):
    # /home/bmercier/Crater/looks/cube/

    path = "/home/bmercier/Crater/looks/cube/{}/{}_{}_look.cube".format(seq.upper(), seq.upper(), shot.upper())
    if os.path.isfile(path):
        return True
    return False

form = cgi.FieldStorage()

db = mysql.connect("nas", "tianhuo", "tianhuo", "skyfire")
c = db.cursor()

idx = 160
if form.has_key("idx"):
    idx = form.getvalue("idx")

linux = False
if form.has_key("linux"):
    linux = form.getvalue("linux")

qry = """

        SELECT q.name, s.name, f.path, f.frange, f.colorspace
          FROM fileset f, seq q, shot s, playitems
         WHERE f.shot=s.idx and s.seq=q.idx and playitems.take=f.idx and playitems.plist={idx}
      ORDER BY q.name, s.name

      """.format(idx=idx)

c.execute(qry)
results = c.fetchall()

sys.stdout.write('Content-type: text/html\n')
sys.stdout.write('\n')

s = rvSession.Session()
seq1 = s.newNode("Sequence", "sequence1")

attrdict = dict()
for row in results:
    # /net/nas/Finals/af0122/0040/af0122_0040_comp_v010,1000-1088
    seq = row[0]
    shot = row[1]
    base = os.path.basename(row[2])
    if linux:
        path = row[2].replace("/share/Finals", "/net/nas/Finals")
    else:
        path = row[2].replace("/share/Finals", "h:/Skyfire")
    fs, fe = row[3].split("-")
    fullpath = "{}/{}.{}-{}#.exr".format(path, base, int(fs)+1, fe)
    src = s.newNode("Source", base)
    src.setMedia(fullpath)
    seq1.addInput(src)

    attrdict.update({ src.name: { "colorspace": "{}".format(row[4]),
                                  "seq": seq,
                                  "shot": shot } })

tempfile = "/tmp/xx{}.rv".format(os.getpid())

s.write(tempfile)

patterns = ['^sourceGroup(\d\d\d\d\d\d)_lookPipeline\s+:',
            '^sourceGroup(\d\d\d\d\d\d)_lookPipeline_0\s+:',
            '^sourceGroup(\d\d\d\d\d\d)_tolinPipeline\s+:',
            '^sourceGroup(\d\d\d\d\d\d)_tolinPipeline_0\s+:']

state = 0
outstr = ""
with open(tempfile) as fi:
    for line in fi:
        if state is 0:
            m = re.match('^sourceGroup(\d\d\d\d\d\d)\s+:\s+RVSourceGroup', line)
            if m:
                groupnum = m.group(1)
                groupname = "sourceGroup{}".format(groupnum)

                if attrdict.has_key(groupname) and attrdict.get(groupname).get("colorspace") == "1":
                    seq  = attrdict.get(groupname).get("seq")
                    shot = attrdict.get(groupname).get("shot")
                    with open("/var/www/ociotemplate.txt") as ti:
                        for line2 in ti:
                            line2 = line2.replace("000000", groupnum)
                            line2 = line2.replace("XXXSEQ", seq.upper())
                            line2 = line2.replace("XXXSHOT", shot.upper())
                            if hasCube(seq, shot):
                                line2 = line2.replace("XXXLOOK", "shot_specific_look")
                            else:
                                line2 = line2.replace("XXXLOOK", "")
                            outstr += line2

            found = False
            groupname = None
            for pat in patterns:
                m = re.match(pat, line)
                if m:
                    groupname = "sourceGroup{}".format(m.group(1))
                    found = True
                    break

            if found:
                if attrdict.has_key(groupname) and attrdict.get(groupname).get("colorspace") == "1":
                    state = 1

            if state is 0:
                outstr += line.replace("\n", "\r\n")

        if state is 1:
            if line[0] == '}':
                state = 0

os.unlink(tempfile)

sys.stdout.write(json.dumps({"data": outstr}))
