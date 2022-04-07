from functions import get_kml, create_extendeddata, create_schemadata, save_kml
import os

NAMESPACE = '{http://www.opengis.net/kml/2.2}'

if __name__ == "__main__":
    path = "E:\\afterFIT_intern\\data\\winddata"
    for root, _, files in os.walk(path):
        if os.path.abspath(root) == os.path.abspath(path):
            for file in files:
                if file[-4:] != '.kml':
                    continue
                print("\r%s" % (file), end='')
                doc = get_kml(os.path.join(root, file))

                # create Schema
                id = file.strip('.kml')
                fields = [{'type': 'float', 'name': '70m'},
                          {'type': 'float', 'name': '50m'},
                          {'type': 'float', 'name': '30m'}]
                schema = create_schemadata(id, fields)
                doc.getroot()[0].Document.getchildren()[0].addnext(schema)

                # insert ExtendedData
                for attr in doc.getroot()[0].iterfind(".//" + NAMESPACE + "Placemark"):
                    info_dict = {}
                    styleId = attr.styleUrl.text.strip('#')
                    style = doc.getroot()[0].find(".//" + NAMESPACE + "Style[@id='" + styleId + "']")
                    info = str(style.BalloonStyle.__getattr__('text').text).strip('年平均風速\n').split('\n')
                    for item in info:
                        temp = item.strip(' m/s').strip('地上高 ').split(': ')
                        info_dict[temp[0]] = temp[1]
                    attr.name.addnext(create_extendeddata(id, info_dict))

                # remove BalloonStyle
                for attr in doc.getroot()[0].iterfind(".//" + NAMESPACE + "Style"):
                    attr.remove(attr.BalloonStyle)

                #save
                save_kml(doc, os.path.join(path, 'edited'), file)

    print('\rfinished!!!!!!')