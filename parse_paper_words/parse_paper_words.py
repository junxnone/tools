import os
import sys
import re
import pandas as pd
from tqdm import tqdm
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
sys.path.append('../google_translate/')
from google_translate import google_translator


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
    parser.add_argument("-k",
                        "--knows_words",
                        help="knows words file path",
                        required=False,
                        default='knows.txt',
                        type=str)
    return parser


def write_list2txt(wlist, file_path):
    with open(file_path, 'w') as fn:
        for line in wlist:
            fn.write(str(line) + '\n')


def read_txt2list(file_path):
    wlist = []
    with open(file_path, 'r') as fn:
        flines = fn.readlines()
        for line in flines:
            wlist.append(line.strip('\n'))
    return wlist


def parse_words(rep_str, words):
    rep = dict((re.escape(k), v) for k, v in rep_str.items())
    pattern = re.compile("|".join(rep.keys()))
    pstr = pattern.sub(lambda m: rep[re.escape(m.group(0))], words)
    return pstr


def load_file2dict(filename):
    odict = {}
    with open(filename, 'r') as fn:
        flines = fn.readlines()
        for line in flines:
            temp = line.strip('\n')
            odict[temp] = ''
    odict['\n'] = ''
    odict['\x0c'] = ''
    return odict


if __name__ == '__main__':
    args = build_argparser().parse_args()
    if not os.path.exists(args.input):
        print('invalid input paper path')
        sys.exit(1)
    if not os.path.exists(args.filter_char):
        print('invalid filter character file path')
        sys.exit(1)
    replace_str = load_file2dict(args.filter_char)
    pagenos = set()
    maxpages = 15
    password = b''
    caching = True
    rotation = 0
    laparams = LAParams()
    rsrcmgr = PDFResourceManager(caching=caching)
    outfp = open(args.output, 'w', encoding='utf-8')

    device = TextConverter(rsrcmgr, outfp, laparams=laparams, imagewriter=None)

    with open(args.input, 'rb') as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp,
                                      pagenos,
                                      maxpages=maxpages,
                                      password=password,
                                      caching=caching,
                                      check_extractable=True):
            page.rotate = (page.rotate + rotation) % 360
            interpreter.process_page(page)

    device.close()
    outfp.close()

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
                lawds[i] = istr.replace('-', '') + lawds[i + 1]
                tmp_words.append(lawds[i])
                lawds[i + 1] = lawds[i]
            elif istr.startswith('http'):
                continue
            else:
                tmp_words.append(lawds[i])
        slawds = set(tmp_words)
    write_list2txt(list(slawds), args.output)

    if os.path.exists(args.knows_words):
        kwd = read_txt2list(args.knows_words)
        tran_wds = slawds - set(kwd)
    else:
        tran_wds = slawds
    print(f'Will Translate {len(tran_wds)} words...')
    gt = google_translator('zh-cn')
    pbar = tqdm(list(tran_wds))
    tdf = pd.DataFrame()
    for wd in pbar:
        result = gt.translate(wd)
        pbar.set_description(
            f"Translating : {wd} - {result['translatedText']}")
        tdf = tdf.append(result, ignore_index=True)
        ftdf = tdf.loc[:, ['input', 'translatedText']]
    ftdf.rename(columns={'input': 'en', 'translatedText': 'zh'}, inplace=True)
    ftdf.to_csv(args.output + '.csv')
