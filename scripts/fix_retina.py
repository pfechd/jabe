import xml.etree.ElementTree as ET
import sys
import os

if sys.platform == "darwin":
    app_path = 'dist/main.app/Contents'
    if os.path.exists(app_path):
        tree = ET.parse(os.path.join(app_path, 'Info.plist'))
        root = tree.getroot()[0]
        child1 = ET.Element('key')
        child1.text = 'NSPrincipalClass'

        child2 = ET.Element('string')
        child2.text = 'NSApplication'

        child3 = ET.Element('key')
        child3.text = 'NSHighResolutionCapable'

        child4 = ET.Element('true')

        root.append(child1)
        root.append(child2)
        root.append(child3)
        root.append(child4)

        tree.write(os.path.join(app_path, 'Info.plist'))        