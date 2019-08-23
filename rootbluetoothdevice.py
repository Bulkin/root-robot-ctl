import gatt
import threading

import rootprotocol as rp

# BLE UUID's
root_identifier_uuid = '48c5d828-ac2a-442d-97a3-0c9822b04979'
uart_service_uuid = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
tx_characteristic_uuid = '6e400002-b5a3-f393-e0a9-e50e24dcca9e' # Write
rx_characteristic_uuid = '6e400003-b5a3-f393-e0a9-e50e24dcca9e' # Notify


class RootDeviceManager(gatt.DeviceManager):
    def send_command(self, data):
        data[2] = self.counter
        data[-1] = rp.crc8(data[:-1])
        self.counter = (self.counter + 1) % 256
        self.robot.tx_characteristic.write_value(data)
        return data[:3]

    def connect(self, result_queue):
        self.counter = 0
        self.result_queue = result_queue
        self.start_discovery(service_uuids=[root_identifier_uuid])
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def disconnect(self):
        self.send_command(rp.build_command('disconnect', 0))
        self.stop()
        self.robot.disconnect()
        self.thread.join()

    # overloaded methods
    def device_discovered(self, device):
        print("[%s] Discovered: %s" % (device.mac_address, device.alias()))
        self.stop_discovery() # Stop searching
        self.robot = RootBluetoothDevice(mac_address=device.mac_address, manager=self)
        self.robot.connect()



class RootBluetoothDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()
        print("[%s] Resolved services" % (self.mac_address))

        self.uart_service = next(
            s for s in self.services
            if s.uuid == uart_service_uuid)

        self.tx_characteristic = next(
            c for c in self.uart_service.characteristics
            if c.uuid == tx_characteristic_uuid)

        self.rx_characteristic = next(
            c for c in self.uart_service.characteristics
            if c.uuid == rx_characteristic_uuid)

        self.rx_characteristic.enable_notifications() # listen to RX messages

        # get root versions
        # useful for populating the result_queue, so the controlling thread
        # can wait on device connection
        self.manager.send_command(rp.build_command('versions',
                                                   rp.board_ids['main']))

    def characteristic_value_updated(self, characteristic, value):
        event = list(map(int, value))
        if event[:2] == [4, 2]: # workaround for incorrect crc in color events
            event[2] = 0
        message = rp.parse_response(event)
        if message.device is not 'color':
            print(message)
        self.manager.result_queue.put(message)
