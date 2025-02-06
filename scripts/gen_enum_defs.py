#!/usr/bin/env python3

import sys
import re

header = \
"""/*
 * WARNING: This file is autogenerated from scripts/gen_enum_defs.py.
 */

#ifndef __ENUM_DEFS_AUTOGEN_H__
#define __ENUM_DEFS_AUTOGEN_H__

"""

footer = \
"""
#endif /* __ENUM_DEFS_AUTOGEN_H__ */
"""

def is_enum_begin(toks):
    if len(toks) == 2:
        # enum {
        if toks[0] == "enum" and toks[-1] == "{":
            return True
    elif len(toks) == 3:
        # typedef enum {
        if toks[0] == "typedef" and toks[1] == "enum" and toks[2] == "{":
            return True
        # enum XXX {
        if toks[0] == "enum" and toks[-1] == "{":
            return True
    return False

def get_enum_val(line):
    toks = re.split(" |\t|\n|=|,", line)
    toks = list(filter(lambda tok: tok != "", toks))
    if len(toks) == 2:
        # x = 3,
        return (toks[0], toks[1])
    elif len(toks) == 1:
        # x,
        return (toks[0], None)
    return (None, None) 

def is_enum_end(toks):
    if len(toks) == 1:
        # };
        if toks[0] == "};":
            return True;
    elif len(toks) >= 2:
        # } XXX;
        # } XXX: 8;
        if toks[0] == "}" and toks[-1][-1] == ";":
            return True
    return False

def gen_enum_header(f):
    print(header, file = f)

def gen_enum_have(f, enum):
    print("#define HAVE_%s" % (enum), file = f)

def gen_enum_footer(f):
    print(footer, file = f)

def gen_enum_defs(vmlinux_h, enum_defs_h, prefixes):
    STAT_UNKNOWN = 0
    STAT_ENUM = 1
    stat = STAT_UNKNOWN
    with open(vmlinux_h, "r") as fv:
        with open(enum_defs_h, "w") as fe:
            gen_enum_header(fe)
            for line in fv:
                line = line.strip()
                toks = line.split()

                if stat == STAT_UNKNOWN:
                    if is_enum_begin(toks):
                        stat = STAT_ENUM
                        continue
                elif stat == STAT_ENUM:
                    if is_enum_end(toks):
                        stat = STAT_UNKNOWN
                        continue
                    (enum, val) = get_enum_val(line)
                    if enum == None:
                        continue
                    for prefix in prefixes:
                        if enum.startswith(prefix):
                            gen_enum_have(fe, enum)
                            break
            gen_enum_footer(fe)

def parse_args(args):
    if len(args) != 2:
        print("usage: gen_enum_defs.py [vmlinux.h] [enum_defs.autogen.h]")
        print("")
        print("Helper script for autogenerating an enum definition header from vmlinux.h.")
        exit(1)
    return (args[0], args[1])

"""
    Helper script for autogenerating an enum definition header.
"""
if __name__ == "__main__":
    (vmlinux_h, enum_defs_h) = parse_args(sys.argv[1:])
    gen_enum_defs(vmlinux_h, enum_defs_h, ["SCX_", "__SCX_"])
    

