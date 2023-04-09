import device

sut = device.Device('/root/devices/GKACY489.xml')
print(sut.identity)
print(sut.board_type)
print(sut.ip_address)
print(sut.user)
print(sut.password)
