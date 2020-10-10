import os
import sys
import re

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter
from argparse import ArgumentParser


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("-i",
                        "--input",
                        help="input pdf paper path",
                        required=True,
                        default='usb',
                        type=str)
    parser.add_argument("-o",
                        "--output",
                        help="output path",
                        required=False,
                        default='out.txt',
                        type=str)
    parser.add_argument("-fc",
                        "--filter_char",
                        help="filter character file path",
                        required=False,
                        default='spc.txt',
                        type=str)
    return parser


def write_list2txt(wlist, file_path):
    with open(file_path, 'w') as fn:
        for line in wlist:
            fn.write(str(line) + '\n')


def parse_words(rep_str, words):
    rep = dict((re.escape(k), v) for k, v in rep_str.items())
    pattern = re.compile("|".join(rep.keys()))
    pstr = pattern.sub(lambda m: rep[re.escape(m.group(0))], words)
    return pstr


if __name__ == '__main__':
    args = build_argparser().parse_args()
    if not os.path.exists(args.input):
        log.error('invalid input paper path')
        sys.exit(1)

    pagenos = set()
    maxpages = 15
    password = b''
    caching = True
    rotation = 0
    laparams = LAParams()
    rsrcmgr = PDFResourceManager(caching=caching)
    outfp = open(args.output, 'w', encoding='utf-8')

    device = TextConverter(rsrcmgr, outfp, laparams=laparams,
                                   imagewriter=None)

    with open(args.input, 'rb') as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            page.rotate = (page.rotate+rotation) % 360
            interpreter.process_page(page)

    device.close()
    outfp.close()

        
    replace_str = {'\n':'',
               ' ':'', 
               '.':'',
              ',':'',
               '[':'',
               ']':'',
               '%':'',
                '{':'',
                '}':'',
                "‘":'',
                "’":'',
                '“':'',
                '”':'',
               '\x0c':'',
               '(':'', 
                '#':'',
                '·':'',
                ':':'',
               ')':''}


    num_pattern = re.compile('[0-9]+')

    with open(args.output, 'r', encoding='utf-8') as wf:
        lines = wf.readlines()
        all_words = []
        for line in lines:
            all_words.extend(line.split(' '))

        lawds = []
        for wd in all_words:
            wdp = parse_words(replace_str, wd)
            if num_pattern.findall(wdp):
                continue
            if len(wdp) > 1:
                lawds.append(wdp.lower())
        tmp_words = []

        for i, istr in enumerate(lawds[:]):
            if istr.endswith('-'):
                lawds[i] = istr.replace('-', '') + lawds[i+1]
                tmp_words.append(lawds[i])
                lawds[i+1] = lawds[i]
            elif istr.startswith('http'):
                continue
            else:
                tmp_words.append(lawds[i])
        slawds = set(tmp_words)
    write_list2txt(list(slawds), args.output)
