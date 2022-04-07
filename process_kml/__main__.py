from functions import process_kml, create_parent
from perfectures import perfecture_dict
import argparse
from os.path import isfile, isdir, join, basename, exists
from os import walk, system, mkdir
import sys

if __name__ == '__main__':
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('Path',
                           metavar='path',
                           type=str,
                           help='Path to KML file. If bulk, input path where all the folders are located.')
    my_parser.add_argument('-b',
                           '--bulk',
                           action='store_true',
                           help='Activate bulk mode.')
    my_parser.add_argument('-p',
                           '--perfecture',
                           type=str,
                           help='Define the perfecture name if Bulk is not activated.')
    my_parser.add_argument('-a',
                           '--area_name',
                           type=str,
                           help='Define the area name for creating parent file.')
    my_parser.add_argument('-f',
                           '--filename',
                           type=str,
                           help='Define the Filename name if Bulk is not activated.')
    my_parser.add_argument('-o',
                           '--output_dir',
                           type=str,
                           help='Define the output dir if Bulk is not activated.')
    my_parser.add_argument('-s',
                           '--split',
                           type=int,
                           help='number of files (required if the file is too big). 0 for autosplit.')
    my_parser.add_argument('--add_color',
                           action='store_true',
                           help='Activate Add Color mode.')
    my_parser.add_argument('--add_region',
                           action='store_true',
                           help='Activate Add Region mode.')
    my_parser.add_argument('--add_style',
                           action='store_true',
                           help='Create Style for polygon area on parent_only creation.')
    my_parser.add_argument('--no_parent',
                           action='store_false',
                           help='Activate "Don\'t create parent file for split KMLs".')
    my_parser.add_argument('--create_parent_only',
                           action='store_true',
                           help='Activate Create Parent Only mode.')
    my_parser.add_argument('--from_parent_files',
                           action='store_true',
                           help='Activate Create Parent Only mode from parent files.')

    # Execute parse_args()
    args = my_parser.parse_args()
    input_path = args.Path
    output_path = args.output_dir
    split = args.split
    filename = args.filename
    area_name = args.area_name

    if output_path:
        if not exists(output_path):
            mkdir(output_path)
        elif not isdir(output_path):
            print('Error! %s: Not a directory.' % output_path)
            sys.exit()

    if (split):
        if split < 0:
            print("Unrecognized split number.")
            sys.exit()

    if args.bulk or args.create_parent_only:
        if not isdir(input_path):
            print('Error! %s: Not a directory.' % input_path)
            sys.exit()
        if args.bulk:
            i = 0
            for root, _, files in walk(input_path, topdown=False):
                for name in files:
                    if name[-4:] == ".kml":
                    # if name[-4:] == ".kml" and name[:-4] == basename(root)[:-4]:
                        i = i + 1
                        system('cls')
                        name = name.split('.kml')[0]
                        print("(%d) %s" % (i, name))
                        if name[:9] in perfecture_dict.keys():
                            perfecture = perfecture_dict[name[:9]]
                        elif name.split('-')[0] in perfecture_dict.values():
                            perfecture = name.split('-')[0]
                            filename = list(perfecture_dict.keys())[list(perfecture_dict.values()).index(perfecture)]
                            try:
                                filename = filename + '-' + name.split('-')[1]
                            except IndexError:
                                filename = filename
                        else:
                            print('cant be performed: filename error.')
                            sys.exit()
                        process_kml(join(root, name+'.kml'),
                                    perfecture=perfecture,
                                    split=split,
                                    add_region=args.add_region,
                                    add_color=args.add_color,
                                    output_path=output_path,
                                    filename=filename,
                                    parent=args.no_parent)
        elif args.create_parent_only:
            if not args.from_parent_files:
                if basename(input_path) in perfecture_dict.values():
                    perfecture = basename(input_path)
                elif basename(input_path)[:9] in perfecture_dict.keys():
                    perfecture = perfecture_dict[basename(input_path)[:9]]
                else:
                    print("Unregistered perfecture name. Please specify perfecture name through '-p' flags.")
                    sys.exit()
            else:
                perfecture = None
            create_parent(input_path,
                          perfecture=perfecture,
                          area_name=area_name,
                          filename=filename,
                          output_path=output_path,
                          from_parent=args.from_parent_files,
                          add_style=args.add_style
                          )




    else:
        if not isfile(input_path) or input_path[-4:] != '.kml':
            print('KML file does not exist or is not a KML file.')
            sys.exit()
        name = basename(input_path).split('.kml')[0]
        if name[:9] in perfecture_dict.keys():
            perfecture = perfecture_dict[name[:9]]
        elif name.split('-')[0] in perfecture_dict.values():
            perfecture = name.split('-')[0]
            filename = list(perfecture_dict.keys())[list(perfecture_dict.values()).index(perfecture)]
            try:
                filename = filename + '-' + name.split('-')[1]
            except IndexError:
                filename = filename
        else:
            print("Unregistered perfecture name. Please specify perfecture name through '-p' flags.")
            sys.exit()
        process_kml(input_path,
                    perfecture,
                    split=split,
                    add_region=args.add_region,
                    add_color=args.add_color,
                    output_path=output_path,
                    filename=filename,
                    parent=args.no_parent)
