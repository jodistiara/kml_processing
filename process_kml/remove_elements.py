from functions import get_kml, save_kml, create_style, create_StyleURL
from metadata import converter
import os

global NAMESPACE = '{http://www.opengis.net/kml/2.2}'

def remove_elem(parent: object, elem_tag: [str, list]):
    if type(elem_tag) == str:
        elem_tag = [NAMESPACE + elem_tag]
    else:
        elem_tag = [NAMESPACE + tag for tag in elem_tag]

    for child in parent.getchildren():
        if child.tag in elem_tag:
            parent.remove(child)
    return parent

def change_minLod(path, minLod, output_path):
    for root, _, files in os.walk(path):
        for name in files:
            doc = get_kml(os.path.join(root, name))
            i = 0
            for i in range(doc.getroot()[0].Document.countchildren()):
                print("\r%s %d" % (name, i))
                if doc.getroot()[0].Document.getchildren()[i].tag != NAMESPACE + "NetworkLink":
                    i = i + 1
                    continue
                else:
                    doc.getroot()[0].Document.getchildren()[i].Region.Lod.minLodPixels = minLod
                    i = i + 1
            save_kml(doc, output_path, name)



if __name__ == "__main__":
    dir = "E:\\afterFIT_インターン\国有林野データ\small-test_child_editmetadata"
    for root, _, files in os.walk(dir):
        for name in files:
            doc = get_kml(os.path.join(root, name))
            n_data = doc.getroot()[0].Document.Folder.countchildren() - 1
            doc.getroot()[0].Document.Folder.name.addnext(
                create_style(
                    line_color="0000ff",
                    line_opacity=1.0,
                    poly_fill=1,
                    poly_color="000000",
                    poly_opacity=0.4,
                    id="0000001"
                )
            )

            i = 0
            for field in doc.getroot()[0].Document.Schema.getchildren():
                doc.getroot()[0].Document.Schema.getchildren()[i].set("name", converter[field.attrib['name']])
                i = i + 1

            i = 1
            for placemark in doc.getroot()[0].Document.Folder.getchildren():

                if placemark.tag != NAMESPACE+"Placemark":
                    continue
                print("\r%s (%d/%d)" % (name, i, n_data), end="")
                new_elem = remove_elem(placemark, ['Style'])
                new_elem.ExtendedData.addnext(
                    create_StyleURL(id = "0000001")
                )
                j = 0
                for simple_data in new_elem.ExtendedData.SchemaData.getchildren():
                    new_elem\
                        .ExtendedData \
                        .SchemaData \
                        .getchildren()[j].set("name", converter[simple_data.attrib['name']])
                    j = j + 1

                doc.getroot()[0].Document \
                    .Folder \
                    .getchildren()[i] = new_elem.__copy__()
                i = i + 1

            save_kml(doc, root, name)

