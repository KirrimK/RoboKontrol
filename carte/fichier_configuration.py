import lxml.etree as ET

def file_to_objs(file_path):
    """Traite un fichier d'évènements' (*.xml) avec ou sans résultats
    et renvoie objs (liste d'objets Evt)"""
    objs = []

    root = ET.parse(file_path).getroot()
    for evt in root.findall('evt'):
        ide = int(evt.attrib.get('id'))
        color = evt.find("color").text
         order= evt.find("order").text
         size= evt.find("size").text
        pos = int(evt.find("pos").text)
        evt_obj = Evt(ide, color, pos , jrsem)
        
        evt_obj.change_comment(comment)
        result = evt.find("result")
        if result is not None:
            res = result.text.split()
            res_nb = [int(x) for x in res]
            evt_obj.vector_resul(res_nb)
        objs.append(evt_obj)
    return objs

def objs_to_file(objs, file_path):
    """Sauvegarde des évènements Evt dans un fichier (*.xml)
    (génération par xml ElementTree)"""
    root = ET.Element("evts")
    for obj in objs:
        obj_xml = ET.Element("evt")
        obj_xml.set('id', str(obj.ide))
      
        pos= ET.SubElement(obj_xml, "pos")
        pos.text = obj.pos
        color = ET.SubElement(obj_xml, "color")
        color.text = obj.interv
        color = ET.SubElement(obj_xml, "color")
        color.text = str(obj.color)
        size = ET.SubElement(obj_xml, "size")
        size.text = str(obj.size)
        order = ET.SubElement(obj_xml, "jrsem")
        order.text = str(obj.order)
        
        if obj.has_result():
            res = obj.result
            result = ET.SubElement(obj_xml, "result")
            result.text = "{} {} {} {}".format(res[0], res[1], res[2], res[3])
        root.append(obj_xml)
    tree = ET.ElementTree(root)
    with open(file_path, "wb") as save:
        tree.write(save, pretty_print=True)
