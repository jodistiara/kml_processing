from functions import get_kml
import os
import pandas as pd

NAMESPACE = '{http://www.opengis.net/kml/2.2}'

if __name__ == "__main__":
    data = {
        "tile_code": [],
        "座標": [],
        "森": [],
        "森のエリア": [],
        "農地": [],
        "農地のエリア": [],
        "高さ30mの風力": [],
        "高さ50mの風力": [],
        "高さ70mの風力": [],
        "日射量": [],
        "平均傾斜角": [],
        "平均標高": [],
        "最低標高": [],
        "最低標高コ": [],
        "最大傾斜方": [],
        "最大傾斜角": [],
        "最小傾斜方": [],
        "最小傾斜角": [],
        "最高標高": []
    }
    file_path = "C:\\Users\\Jodistiara\\Downloads\\MoriAndNissyaryouDataAdded.kml"
    doc = get_kml(file_path)
    i = 1
    for Placemark in doc.getroot()[0].iterfind(".//" + NAMESPACE + "Placemark"):
        for item in data:
            try:
                value = Placemark.ExtendedData.find(
                    './/' + NAMESPACE + "Data[@name='" + item + "']"
                ).value
            except AttributeError:
                if item == 'zahyou':
                    value = Placemark.find('.//' + NAMESPACE + "coordinates")
                elif item == 'tile_code':
                    value = "A" + str(i)
                else:
                    value = ''
            data[item].append(value)
        i = i + 1
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(
        os.path.dirname(file_path),
        os.path.basename(file_path).split('.')[0]+'.csv'
    ))