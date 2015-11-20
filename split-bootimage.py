#!/usr/bin/env python

# like split_bootimage.pl, but also recovers the QC device tree table at the end of the boot image
# (used on some Qualcomm-based Sony Xperia models)
#
# see https://github.com/sonyxperiadev/mkqcdtbootimg for details

import sys
import struct
from collections import namedtuple

def aligned(n, page_size):
    num_pages = (n + page_size - 1)/page_size
    return num_pages*page_size

def dump_part(f_in, filename, offset, size):
    f_out = open(filename, 'wb')

    f_in.seek(offset, 0)
    f_out.write(f_in.read(size))

    f_out.close()

def split_bootimage(filename):
    f = open(filename, 'rb')
    
    header = struct.Struct('8s I I I I I I I I I 4x 16s 512s 8x')
    magic, kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr, tags_addr, page_size, dt_size, name, cmdline = header.unpack(f.read(header.size))

    if magic != 'ANDROID!':
        sys.stderr.write(filename + " is not a valid android boot image\n")
        sys.exit(1)
    
    print 'kernel size : %d' % kernel_size
    print 'kernel addr : 0x%x' % kernel_addr
    print 'ramdisk size: %d' % ramdisk_size
    print 'ramdisk addr: 0x%x' % ramdisk_addr
    print 'second size : %d' % second_size
    print 'second addr : 0x%x' % second_addr
    print 'tags addr   : 0x%x' % tags_addr
    print 'page size   : %d' % page_size
    print 'dt size     : %d' % dt_size
    print 'name        : %s' % name
    print 'cmdline     : %s' % cmdline

    offset = page_size

    if kernel_size > 0:
        dump_part(f, filename + "-zImage", offset, kernel_size)
        offset += aligned(kernel_size, page_size)

    if ramdisk_size > 0:
        dump_part(f, filename + "-ramdisk.gz", offset, ramdisk_size)
        offset += aligned(ramdisk_size, page_size)

    if second_size > 0:
        dump_part(f, filename + "-second", offset, second_size)
        offset += aligned(second_size, page_size)

    if dt_size > 0:
        dump_part(f, filename + "-dt", offset, dt_size)

    f.close()

def main():
    if len(sys.argv) < 2:
        print 'Usage: ' + sys.argv[0] + ' boot.img\n'
        sys.exit(1)

    split_bootimage(sys.argv[1])

if __name__ == '__main__':
    main()
