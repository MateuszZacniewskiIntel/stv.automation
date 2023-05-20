from api import ssh_manager
import configparser
import uuid


class FileManager:

    def __init__(self, device=ssh_manager.Dummy()):
        self.device = device

    def download_driver(self, driver_link):
        driver_tar_file = driver_link.split('/')[-1]
        driver_ver = driver_tar_file.replace('.tar.gz', '')
        password = ''
        self.device.run_command(f'rm -rf /root/drivers/{driver_ver}')
        self.device.run_command(f'mkdir -p /root/drivers/{driver_ver}')
        self.device.run_command(f'wget --output-file=/dev/stdout {driver_link} --user sys_swfauto --password {password} -P /tmp/{driver_ver} --no-check-certificate')
        self.device.run_command(f'mv -f /tmp/{driver_ver} /root/drivers/')

    def unzip_driver(self, driver_ver):
        self.device.run_command(f'tar zxf /root/drivers/{driver_ver}/{driver_ver}.tar.gz -C /root/drivers/{driver_ver}/')


class FileManagerHost(FileManager):

    def __init__(self, device):
        super().__init__(device)

    # Method that downloads the virtual network configuration file
    def download_virutal_network_config(self):
        self.device.run_command(f'cd /var/lib/libvirt/images && '
                                'wget http://10.237.149.35/stv_test_network.xml')

    # Method that downloads virtual disk image file
    def create_vm_image(self, vm_name):
        output = self.device.run_command('ls -l /var/lib/libvirt/images/centosstream8.zip')
        if 'centosstream8.zip' not in output:
            self.device.run_command('cd /var/lib/libvirt/images && '
                                    'wget -q -T600 http://10.237.149.35/centosstream8.zip')
        output = self.device.run_command(f'ls -l /var/lib/libvirt/images/{vm_name}.img')
        if vm_name not in output:
            self.device.run_command(f'cd /var/lib/libvirt/images && '
                                    f'unzip centosstream8.zip')
            self.device.run_command(f'mv /var/lib/libvirt/images/centosstream8.img /var/lib/libvirt/images/{vm_name}.img')

    # Method that creates configs for each defined guest machine.
    # Xml file is being created for each machine, and it's deta is updated for vm name, random uuid,
    # qemu path, virtual disk image path and a mac address.
    def create_vm_config(self, vm_name):
        self.device.run_command(f'cd /var/lib/libvirt/images && '
                                'wget http://10.237.149.35/vm_config_template.xml')
        self.device.run_command(f'cd /var/lib/libvirt/images/ && '
                                f'mv vm_config_template.xml {vm_name}.xml')
        qemu_list = self.device.run_command('whereis qemu-kvm')
        qemu_list = qemu_list.rstrip('\n')
        qemu_list = qemu_list.split(' ')
        qemu_list.remove('qemu-kvm:')
        qemu_kvm_path = ""
        for q in qemu_list:
            qemu = q.rstrip('/qemu-kvm')
            output = self.device.run_command(f'ls -l {qemu} | grep qemu-kvm')
            if output[0] == '-':
                qemu_kvm_path = f'{qemu}/qemu-kvm'
                break
        output = self.device.run_command(f'cat /var/lib/libvirt/images/stv_test_network.xml | grep {vm_name}')
        mac = output.split('\'')[1]
        self.device.run_command(f'sed -i \'s@vm_name@{vm_name}@g\' /var/lib/libvirt/images/{vm_name}.xml')
        self.device.run_command(f'sed -i \'s@vm_uuid@{uuid.uuid4()}@g\' /var/lib/libvirt/images/{vm_name}.xml')
        self.device.run_command(f'sed -i \'s@path-qemu-kvm@{qemu_kvm_path}@g\' /var/lib/libvirt/images/{vm_name}.xml')
        self.device.run_command(f'sed -i \'s@vm_image.img@{vm_name}.img@g\' /var/lib/libvirt/images/{vm_name}.xml')
        self.device.run_command(f'sed -i \'s@aa:bb:cc:dd:ee:ff@{mac}@g\' /var/lib/libvirt/images/{vm_name}.xml')


class FileManagerGuest(FileManager):

    def __init__(self, device):
        super().__init__(device)
