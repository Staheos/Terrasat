#!/usr/bin/env python3

""" This program sends a response whenever it receives the "INF" """
import queue
# Copyright 2018 Rui Silva.
#
# This file is part of rpsreal/pySX127x, fork of mayeranalytics/pySX127x.
#
# pySX127x is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pySX127x is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving pySX127x without disclosing the source code of your
# own applications, or shipping pySX127x with a closed source product.
#
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.

import queue
import time
from SX127x.LoRa import LoRa2 as LoRa
# from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD2 as BOARD
from SX127x.constants import MODE, BW, CODING_RATE
from util import *


BOARD.setup()
BOARD.reset()


# parser = LoRaArgumentParser("Lora tester")


class mylora(LoRa):
    def __init__(self, packet_queue, verbose=True):
        super(mylora, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.var = 0
        self.packet_queue = packet_queue

    def on_rx_done(self):
        BOARD.led_on()
        print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)  # Receive INF
        print(f"Recv payload: {payload}")
        mens = bytes(payload).decode("utf-8", 'ignore')
        mens = mens[2:-1]  # to discard \x00\x00 and \x00 at the end
        print(mens)
        BOARD.led_off()
        if mens == "INF":
            print("Received data request INF")
            time.sleep(1)
            packet = ""
            for _ in range(0, 10):
                if self.packet_queue.empty():
                    break
                packet += self.packet_queue.get(block=True, timeout=1)
            print(f"Empty: {self.packet_queue.qsize()}")
            self.packet_queue.task_done()
            print("Sending: " + str(packet))
            sending_payload = get_message_bytes(packet)
            print("Sending payload: " + str(sending_payload))
            # sending_payload = [255, 255, 0, 0, 68, 65, 84, 65, 32, 82, 65, 83, 80, 66, 69, 82, 82, 89, 32, 80, 73, 0]
            # print("Sending payload: " + str(sending_payload))
            print("Sent payload: " + str(self.write_payload(sending_payload)))
            self.set_mode(MODE.TX)
        elif mens == "ACK":
            print("Received ACK")
        time.sleep(1)
        self.var = 1
        # self.reset_ptr_rx()
        # self.set_mode(MODE.RXCONT)

    def on_tx_done(self):
        print("\nTxDone")
        print(self.get_irq_flags())

    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())
        self.var = 1

    def on_rx_timeout(self):
        print("\non_RxTimeout")
        print(self.get_irq_flags())
        self.var = 1

    def on_valid_header(self):
        print("\non_ValidHeader")
        print(self.get_irq_flags())

    def on_payload_crc_error(self):
        print("\non_PayloadCrcError")
        print(self.get_irq_flags())

    def on_fhss_change_channel(self):
        print("\non_FhssChangeChannel")
        print(self.get_irq_flags())

    def start(self):
        while True:
            self.var = 0
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)  # Receiver mode
            while self.var == 0:
                time.sleep(0.1)
            print("Resetting loop")
