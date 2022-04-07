from functions import get_kml
from pykml.factory import KML_ElementMaker as kml
import numpy as np

def getPolygonCoordinates(kml_doc):
    '''
    Summary: to get the list of all polygon's coordinates inside a KML file
    @param kml_doc: extracted kml file
    @param
    return numpy 2d arrays of [lat_list, lon_list]
    '''
    coordinates = ''
    lat_lon = []

    for placemark in kml_doc.getroot()[0].Folder.Document.Folder.getchildren():

        if placemark.tag != "{http://www.opengis.net/kml/2.2}Placemark":
            continue
        polygon = placemark.MultiGeometry.Polygon
        while polygon != None:
            linear_ring = placemark.MultiGeometry.Polygon.outerBoundaryIs.LinearRing
            while linear_ring != None:
                coordinates = (coordinates + ' '
                               + linear_ring.coordinates.text).strip('\n').strip('\t').strip(' \n').strip(' \t')
                linear_ring = linear_ring.getnext()
            polygon = polygon.getnext()
        coordinates = coordinates.split(' ')

        for coor in coordinates:
            coor = [float(x) for x in coor.split(',')]
            lat_lon.append(coor[::-1][-2:])

    return np.array(lat_lon)

def get_files_from_area(kml_file):
    files = []
    for network_link in kml_file.getroot()[0].Document.getchildren():
        if network_link.tag != "{http://www.opengis.net/kml/2.2}NetworkLink":
            continue
        file = network_link.Link.href.text
        file = ''.join(file.split('_ov'))
        files.append(file)

    return files


def getMeshCoordinateList(kml_doc, existing_mesh: np.asarray=None):
    '''
    Summary: to get the list of all polygon's coordinates inside a KML file
    @param kml_doc: extracted kml file
    @param
    return numpy 2d arrays of [lat_list, lon_list]
    '''
    lats = []
    lons = []
    for placemark in kml_doc.getroot()[0].Document.Document.getchildren():

        if placemark.tag != "{http://www.opengis.net/kml/2.2}Placemark":
            continue
        coordinates = (placemark
                       .Polygon
                       .outerBoundaryIs
                       .LinearRing
                       .coordinates.text)  # coordinates
        coordinates = coordinates.strip('\n').strip('\t').strip(' \n').strip(' \t')
        coordinates = np.array(coordinates.split(' '))

        for coor in coordinates:
            coor = [float(x) for x in coor.split(',')]
            lons.append(coor[0])
            lats.append(coor[1])

    return np.array(lats), np.array(lons)


def getNearestLatLon(lat, lon, message):
    """
    概要: 指定した緯度経度から最も近いメッシュ上の緯度経度を算出する
    @param lat: 対象の緯度
    @param lon: 対象の経度
    @param message: 対象のpygrib.gribmessage
    @return 対象値に最も近いメッシュ上のlat,lon
    """

    # メッシュ上のlatとlonのリストを作成
    lats, lons = message.latlons()
    lat_list = []
    for n in range(0, len(lats)):
        tmp = lats[n][0]
        lat_list.append(float(tmp))
    lon_list = lons[0]

    # リスト要素と対象値の差分を計算し最小値の値を取得
    lat_near = lat_list[np.abs(np.asarray(lat_list) - lat).argmin()]
    lon_near = lon_list[np.abs(np.asarray(lon_list) - lon).argmin()]

    return lat_near, lon_near


def list_to_coordinates(list):
    str = ''
    for item in list:
        str = str + ','.join(item) + ',0.0 '
    return str


if __name__ == "__main__":
    doc = get_kml("E:\\afterFIT_インターン\\全国保安林国有林融合 (1).kml")
    wind_data_dir = "E:\\afterFIT_インターン\全国風力データ\\"

    files = get_files_from_area(wind_data_dir + "Area02.kml")
    mesh_coordinate_list = np.array
    lats = np.array([], np.float64)
    lons = np.array([], np.float64)
    for file in files:
        mesh_doc = get_kml(wind_data_dir + file)
        lats, lons = getMeshCoordinateList(mesh_doc)

    # print(getPolygonCoordinates(doc))