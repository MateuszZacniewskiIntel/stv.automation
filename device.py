import xml.etree.ElementTree as ET
import os


class Device:

    def __init__(self, device_xml):
        device_xml_tree = ET.parse(device_xml)
        device_xml_root = device_xml_tree.getroot()
        try:
            self.identity = device_xml_root.find('unicode/[@name="identity"]').text
            self.board_type = device_xml_root.find('unicode/[@name="type_"]').text
            self.ip_address = device_xml_root.find('./SSHProtocol/unicode/[@name="host"]').text
            self.user = device_xml_root.find('./SSHProtocol/User/unicode/[@name="name"]').text
        except AttributeError:
            print('Device XML is missing some data!')

        try:
            self.password = device_xml_root.find('./SSHProtocol/User/unicode/[@name="password"]').text
        except AttributeError:
            print('Password is not set in device XML.')
            print('Using PASSWORD environment variable instead.')
            try:
                self.password = os.environ['PASSWORD']
            except KeyError as err:
                print(f'Environment variable {err} is not set')
                print('To set password in system environment use:')
                print('export PASSWORD=host_password')