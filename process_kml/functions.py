from pykml.factory import KML_ElementMaker as kml
from pykml import parser
from lxml import objectify
from lxml.etree import tostring
from zipfile import ZipFile, ZIP_DEFLATED
from os.path import join, basename, exists, dirname
from os import mkdir, walk, rename
from math import ceil, floor
from shutil import move
from perfectures import perfecture_dict


def get_kml(kml_file, encoding='utf-8'):
    f = open(kml_file, 'r', encoding=encoding)
    return parser.parse(f)


def get_coordinates(raw_coordinates):
    # first element -> horizontal line
    # second element -> vertical line
    n, s, w, e = 0, 0, 0, 0
    if type(raw_coordinates) == str:
        raw_coordinates = raw_coordinates.split(' ')

    for coor in raw_coordinates:
        if type(coor) == str:
            coor = [float(x) for x in coor.split(',')]
        if n + s + w + e == 0:
            w = coor[0]
            e = coor[0]
            n = coor[1]
            s = coor[1]
        else:
            if coor[0] < w:
                w = coor[0]
            elif coor[0] > e:
                e = coor[0]
            if coor[1] > n:
                n = coor[1]
            elif coor[1] < s:
                s = coor[1]
    return [[e, n], [w, s]]


def create_color(color: str = "000000", opacity: float = 0.5):
    kml_color = kml.color(hex(floor(255 * opacity))[-2:] + color)
    objectify.deannotate(kml_color, cleanup_namespaces=True, xsi_nil=True)
    return kml_color


def create_style(create_linestyle=True, create_polystyle=True,
                 line_color="000000", line_opacity=0.5, line_color_mode="normal",
                 poly_color="ffffff", poly_opacity=0.5, poly_color_mode="normal", poly_fill=True,
                 poly_outline=True, id: str = None):
    line = None
    poly = None
    if create_linestyle:
        line = kml.LineStyle(
            create_color(line_color, line_opacity)
            # ,kml.colorMode(line_color_mode)
        )
    if create_polystyle:
        poly = kml.PolyStyle(
            create_color(poly_color, poly_opacity),
            # kml.colorMode(poly_color_mode),
            kml.fill(int(poly_fill)),
            kml.outline(int(poly_outline))
        )
    style = kml.Style(
        line, poly
    )
    if id and type(id) == str:
        style.set("id", id)
    objectify.deannotate(style, cleanup_namespaces=True, xsi_nil=True)
    return style


def create_StyleURL(id: str):
    styleURL: object = kml.styleUrl('#' + id)
    objectify.deannotate(styleURL, cleanup_namespaces=True, xsi_nil=True)
    return styleURL


def create_region(point, minLod=128, maxLod=-1):
    region = kml.Region(
        kml.LatLonAltBox(
            kml.north(point[0][1]),
            kml.south(point[1][1]),
            kml.west(point[1][0]),
            kml.east(point[0][0])
        ),
        kml.Lod(
            kml.minLodPixels(minLod),
            kml.maxLodPixels(maxLod)
        )
    )
    objectify.deannotate(region, cleanup_namespaces=True, xsi_nil=True)
    return region


def create_networklink(point: list, path: str, name: str, visibility: bool = True, add_region: bool = True,
                       minLod: int = 128, maxLod: int = -1):
    if add_region:
        networklink = kml.NetworkLink(kml.name(name),
                                      kml.visibility(int(visibility)),
                                      create_region(point, minLod, maxLod),
                                      kml.Link(kml.href(path),
                                               kml.viewRefreshMode('onRegion')))
    else:
        networklink = kml.NetworkLink(kml.name(name),
                                      kml.visibility(int(visibility)),
                                      kml.Link(kml.href(path),
                                               kml.viewRefreshMode('onRegion')))

    return networklink


def create_schemadata(id: str, fields: list):
    schemadata = kml.Schema(
        name = id,
        id = id
    )
    for field in fields:
        schemadata.addattr('SimpleField', '')
        for key, value in field.items():
            schemadata.getchildren()[-1].set(key, value)
    objectify.deannotate(schemadata, cleanup_namespaces=True, xsi_nil=True)
    return schemadata


def create_extendeddata(id: str, fields: dict):
    extendeddata = kml.ExtendedData(
        kml.SchemaData(
            schemaUrl="#"+id
        )
    )
    for key, value in fields.items():
        extendeddata.SchemaData.addattr('SimpleData', value)
        extendeddata.SchemaData.getchildren()[-1].set('name', str(key))

    objectify.deannotate(extendeddata, cleanup_namespaces=True, xsi_nil=True)
    return extendeddata



def generate_kml(name, number_of_kmls=1, doc_root=None, parent=False):
    docs = []
    if parent:
        return kml.kml(kml.Document(kml.name(name)))
    else:
        schema = doc_root.getchildren()[0].getchildren()[0].__copy__()
        if number_of_kmls == 1:
            folder = kml.Folder(kml.name(name))
            docs.append(kml.kml(
                kml.Document(
                    schema.__copy__(),
                    folder.__copy__()
                )
            ))
        else:
            for i in range(number_of_kmls):
                folder = kml.Folder(kml.name(name + "-" + str(i + 1)))
                docs.append(kml.kml(
                    kml.Document(
                        schema.__copy__(),
                        folder.__copy__()
                    )
                ))
        return docs


def save_kml(doc, dirpath, filename):
    outfile = open(join(dirpath, filename),
                   'w', encoding='utf-8')
    outfile.write(tostring(doc,
                           pretty_print=True,
                           xml_declaration=True,
                           encoding='utf-8').decode('utf-8'))
    outfile.close()


def zip_kml(output_path: str, filename):
    zipObject = ZipFile(filename + '.kmz', 'w', ZIP_DEFLATED)
    for root, _, files in walk(output_path):
        for name in files:
            filepath = join(root, name)
            zipObject.write(filepath, basename(filepath))
    zipObject.close()
    move(filename + '.kmz', dirname(output_path))
    rename(join(dirname(output_path), filename + '.kmz'), join(dirname(output_path), basename(output_path) + '.kmz'))


def create_parent(input_dir: str, perfecture: str = None, area_name: str = None, filename: str = None,
                  output_path: str = None,
                  from_parent: bool = False, add_style: bool = True):
    coordinate_list = []
    i = 0
    if not filename and not area_name:
        filename = basename(input_dir) + "_parent"
        area_name = filename
    elif not filename and area_name:
        filename = area_name
    elif filename and not area_name and not perfecture:
        area_name = filename
    elif not area_name and perfecture:
        area_name = perfecture

    if not output_path:
        output_path = input_dir

    parent = generate_kml(area_name, parent=True)
    if add_style:
        parent.Document.name.addnext(create_style(
            poly_opacity=0.2
        ))

    for root, _, files in walk(input_dir):
        num_of_files = len(files)
        for name in files:
            doc = get_kml(join(root, name))
            part = name.split('.kml')[0].split('-')[-1]
            print('\rDoing %d of %d' % (i + 1, num_of_files), end="")
            if not from_parent:
                network_link_name = perfecture + '-' + part
                try:
                    temp = doc.getroot()[0].Document.Folder
                except AttributeError:
                    num_of_files = num_of_files - 1
                    continue
                for placemark in doc.getroot()[0].Document.Folder.getchildren():

                    if placemark.tag != "{http://www.opengis.net/kml/2.2}Placemark":
                        continue

                    coordinates = get_coordinates(placemark
                                                  .MultiGeometry
                                                  .Polygon
                                                  .outerBoundaryIs
                                                  .LinearRing
                                                  .coordinates.text)  # coordinates
                    coordinate_list.append(coordinates[0].copy())
                    coordinate_list.append(coordinates[1].copy())
            else:
                network_link_name = doc.getroot()[0].Document.name
                for network_link in doc.getroot()[0].Document.getchildren():
                    if network_link.tag != '{http://www.opengis.net/kml/2.2}NetworkLink':
                        continue
                    coordinates = [[float(network_link.Region.LatLonAltBox.east.text),
                                    float(network_link.Region.LatLonAltBox.north.text)],
                                   [float(network_link.Region.LatLonAltBox.west.text),
                                    float(network_link.Region.LatLonAltBox.south.text)]
                                   ]
                    coordinate_list.append(coordinates[0].copy())
                    coordinate_list.append(coordinates[1].copy())

            if (i == 0):
                visibility = True
            else:
                visibility = False

            if not from_parent:
                coordinates = get_coordinates(coordinate_list)
                coordinate_list = []

            parent.Document.getchildren()[-1].addnext(create_networklink(
                point=coordinates,
                path=name,
                name=network_link_name,
                minLod=128,
                maxLod=-1,
                visibility=visibility
            ))
            i = i + 1

    if from_parent:
        coordinates = get_coordinates(coordinate_list)
        parent.Document.name.addnext(create_region(coordinates,
                                                   minLod=0,
                                                   maxLod=256))
        coordinates_str = [coordinates[0].copy(),
                           [coordinates[0][0], coordinates[1][1]],
                           coordinates[1].copy(),
                           [coordinates[1][0], coordinates[0][1]]]
        for x in coordinates_str:
            x.append(0.0)
        coordinates_str = ' '.join([','.join([str(x) for x in y]) for y in coordinates_str])
        parent.Document.Region.addnext(kml.Placemark(kml.name(area_name),
                                                     kml.Polygon(
                                                         kml.outerBoundaryIs(
                                                             kml.LinearRing(
                                                                 kml.coordinates(
                                                                     coordinates_str
                                                                 )
                                                             )
                                                         )
                                                     )))
    save_kml(parent,
             output_path,
             filename + '.kml')


def process_kml(input_path: str, perfecture: str, split: int,
                output_path: str = None, filename: str = None, add_region=True, add_color=True, parent=True):
    print("Load the data...", end="")
    doc = get_kml(input_path)
    try:
        n_data = doc.getroot()[0].Document.Folder.countchildren() - 2
    except AttributeError:
        n_data = 0
    if n_data > 0:
        if split == 0:
            if n_data > 40000:
                split = ceil(n_data / 30000)
            else:
                split = None

        if not (filename):
            filename = basename(input_path).split('.')[0]

        if split:
            chunks = ceil(n_data / split)
            new_docs = generate_kml(perfecture, doc_root=doc.getroot()[0], number_of_kmls=split)

            if parent:
                coordinate_list = []
                if split == 1:
                    part = filename.split('-')[-1]
                    if part == filename:
                        new_docs.append(generate_kml(perfecture, parent=True))
                    else:
                        new_docs.append(generate_kml(perfecture + "-" + part, parent=True))

            if filename in perfecture_dict.values():
                filename = list(perfecture_dict.keys())[list(perfecture_dict.values()).index(filename[:-4])]
            if not output_path and not (exists(join(dirname(input_path), perfecture))):
                mkdir(join(dirname(input_path), perfecture))  # create folder
                output_path = join(dirname(input_path), perfecture)
            elif not output_path and (exists(join(dirname(input_path), perfecture))):
                output_path = join(dirname(input_path), perfecture)
            elif output_path and not exists(output_path):
                mkdir(output_path)

        else:
            if not output_path:
                output_path = dirname(input_path)

        i = 0

        # for i in range(1, n_data):
        for placemark in doc.getroot()[0].Document.Folder.getchildren():

            if placemark.tag != "{http://www.opengis.net/kml/2.2}Placemark":
                continue
            print('\rDoing %d of %d' % (i + 1, n_data), end="")
            coordinates = get_coordinates(placemark
                                          .MultiGeometry
                                          .Polygon
                                          .outerBoundaryIs
                                          .LinearRing
                                          .coordinates.text)  # coordinates

            if add_region:
                region_element = create_region(coordinates,
                                               minLod=128,
                                               maxLod=-1)
            if add_color:
                # color_fill, outline = create_polygon_fill("000000", 0.5)
                color_fill = create_color("000000", 0.5)

            if split:
                if parent:
                    coordinate_list.append(coordinates[0].copy())
                    coordinate_list.append(coordinates[1].copy())
                print(' (%d/%d)' % (((i // chunks) + 1), split), end="")

                if add_region:
                    placemark.Style.addnext(region_element)
                if add_color:
                    placemark.Style.PolyStyle.fill = 1
                    placemark.Style.PolyStyle.fill.addprevious(color_fill)

                new_docs[i // chunks].Document.Folder.getchildren()[-1].addnext(placemark.__copy__())

                if ((i + 1) % chunks) == 0 or (i + 1) == n_data:
                    if split == 1:
                        name = filename + '.kml'
                        network_name = perfecture
                    else:
                        name = filename + "-" + str((i // chunks) + 1) + '.kml'
                        network_name = perfecture + "-" + str((i // chunks) + 1)
                    save_kml(new_docs[i // chunks],
                             output_path,
                             name)
                    if parent:
                        if (i // chunks) == 0:
                            visibility = True
                        else:
                            visibility = False

                        new_docs[-1].Document.getchildren()[-1].addnext(create_networklink(
                            get_coordinates(coordinate_list),
                            name,
                            network_name,
                            minLod=128,
                            maxLod=-1,
                            visibility=visibility,
                            add_region=True
                        ))
                        coordinate_list = []

            else:
                # add region
                if add_region:
                    doc.getroot()[0].Document \
                        .Folder \
                        .getchildren()[i + 1] \
                        .Style \
                        .addnext(region_element)

                # add colorfill
                if add_color:
                    doc.getroot()[0].Document.Folder.getchildren()[i + 1].Style.PolyStyle.fill = 1
                    doc.getroot()[0].Document.Folder.getchildren()[i + 1].Style.PolyStyle.fill.addprevious(color_fill)
                    # doc.getroot()[0].Document.Folder.getchildren()[i + 1].Style.PolyStyle.fill.addnext(outline)

            i = i + 1

        if i > 0:
            if split:
                if parent:
                    save_kml(new_docs[-1],
                             output_path,
                             filename + '_parent.kml')
                # zip_kml(output_path, filename)
            else:
                save_kml(doc, dirname(output_path), filename + '.kml')
            print()
