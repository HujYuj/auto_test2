import os
from lxml import etree as er


class XMLHelper:

    def __init__(self):
        self.xml_doc = None

    def load_xml_document(self, xml_file_path: str) -> None:
        # print(xml_file_path)
        if not os.path.exists(xml_file_path):
            raise FileNotFoundError(f'{xml_file_path} does not exist')
        self.xml_doc = er.parse(xml_file_path)

    def get_nodes(self, node_xpath: str):
        current_nodes = self.xml_doc.xpath(node_xpath)

        return current_nodes

    def get_node_attribute(self, node: er.Element, attribute_name: str) -> str:
        return node.get(attribute_name)

    def get_node_text(self, node: er.Element) -> str:
        return node.text

    def release(self):
        self.xml_doc = None
        del self.xml_doc


if __name__ == '__main__':
    current_xml = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                               'resource', 'RouteCommandsFor5G.xml')
    print(current_xml)
    xml_helper = XMLHelper()
    xml_helper.load_xml_document(current_xml)
    antennaId = 16
    nodes = xml_helper.get_nodes(
        f'//MasterRoutes/TRX[@id={antennaId - 1}]/Beamforming[@isOn="true"]/RouteCommand')
    for command_node in nodes:
        print(command_node.text)
    xml_helper.release()
