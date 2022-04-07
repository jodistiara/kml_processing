### ShapeFileをKMLに交換するためのスクリプト
### スクリプトをQGISのPython Consoleで貼り付けてください。
### filenameとpathを確認して、変更してください。

filename = 'A45-19_'
i = 1
banned = [1,2,5,8]
x = []
while i <= 47:
	if i not in banned:
		if i < 10:
			x.append('0' + str(i))
		else:
			x.append(str(i))
	i = i + 1

dest_crs = QgsCoordinateReferenceSystem(4326)

for i in x:
	path = "E:\\afterFIT - Intern\\" + filename + i + "_GML\\" + filename
	v = QgsVectorLayer(path + i + '.shp')
	if v.isValid():
		v.setProviderEncoding('Shift_JIS')
		QgsVectorFileWriter.writeAsVectorFormat(v, path + i + ".kml", 'UTF-8', dest_crs, 'KML')
	else:
		print(i, " invalid.")



dest_crs = QgsCoordinateReferenceSystem(4326)
path = "E:\\afterFIT - Intern\\全国保安林国有林融合 (1).kml"
vlayer = QgsVectorLayer(path, None, "ogr")
v.isValid()