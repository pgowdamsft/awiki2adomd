#!/usr/bin/env python3

"""
convertwiki.py

Pradeep Gowda
2022-02-21

"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess

assets = ["attachments", "images", "styles"]


def extract_meta(fname):
    with open(fname) as f:
        s = f.read()
    title = author = editor = None
    m = re.search(r"<title>(.*)</title>", s, re.M | re.I)
    if m:
        title = m.group(1)
    m = re.search(r"<span class='author'>(.*)</span>,", s, re.M | re.I)
    if m:
        author = m.group(1)
    m = re.search(r"<span class='editor'>(.*)</span>", s, re.M | re.I)
    if m:
        editor = m.group(1)
    # print(f"title={title}, author={author}, editor={editor}")
    return str(title), author, editor


def replace_stuff(s, replace_stuff):
    for k, v in replace_stuff.items():
        s = s.replace(k, v)
    return s


def main(indir, outdir, replace):
    if os.path.isdir(outdir):
        os.mkdirs(outdir, exist_ok=True)
    for a in assets:
        frm, to = os.path.join(indir, a), os.path.join(outdir, a)
        if os.path.isdir(frm):
            shutil.move(frm, to)
        else:
            print(f"one of these doesnt exist.. from={frm} to={to}")
    infiles = glob.glob(f"{indir}/*.html")
    with replace as rf:
        replace_strings = json.load(rf)
    htmls = [f.replace(f"{indir}/", "") for f in infiles]
    for h in htmls:
        replace_strings[h] = h.replace(".html", ".md")
    for f in infiles:
        bare = "".join(f.split(".")[:-1])
        newname = ".".join([bare, "md"]).replace(indir, outdir)
        print(f"processing {f} -> {newname}")
        title, author, editor = extract_meta(f)
        if author:
            author = author.replace(" (Deactivated)", "")
        if editor:
            editor = editor.replace(" (Deactivated)", "")

        with open(newname, "w") as of:
            output = subprocess.run(
                ["pandoc", "-f", "html", "--lua-filter", "filter.lua", "-t", "gfm", f],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            of.write(f"---\n")
            if title:
                of.write(f"title: {title}\n")
            if author:
                of.write(f"author: {author}\n")
            if editor:
                of.write(f"editor: {editor}\n")
            of.write(f"---\n\n")
            content = replace_stuff(output.stdout, replace_strings)
            of.write(f"{content}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--indir", help="input directory")
    parser.add_argument("-o", "--outdir", help="output directory")
    parser.add_argument(
        "-r",
        "--replace",
        type=argparse.FileType('r'),
        default="replace.json",
        help="JSON file with replacement strings",
    )
    args = parser.parse_args()
    main(args.indir, args.outdir, args.replace)
