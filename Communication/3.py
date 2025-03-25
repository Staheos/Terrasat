#!/usr/bin/env python3

""" This program asks a client for data and waits for the response, then sends an ACK. """
import datetime
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

import sys
import json
import hashlib
import time
from SX127x.LoRa import *
# from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD
from util import *

BOARD.setup()
BOARD.reset()


# parser = LoRaArgumentParser("Lora tester")


class mylora(LoRa):
    def __init__(self, verbose=True):
        super(mylora, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.var = 0

    def on_rx_done(self):
        print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        payload = payload[2:-1]  # to discard \x00\x00 and \x00 at the end
        recv_hash = hashlib.sha1(bytes(payload)).hexdigest()
        print(f"Recv payload: {recv_hash}   {payload}")
        open("received.txt", "a").write(f"{datetime.datetime.now().isoformat()}  " + bytes(payload).decode("utf-8", 'ignore') + "\r\n")
        print(bytes(payload).decode("utf-8", 'ignore'))
        # self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)


    def on_tx_done(self):
        print("\nTxDone")
        print(self.get_irq_flags())

    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())

    def on_rx_timeout(self):
        print("\non_RxTimeout")
        print(self.get_irq_flags())

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
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)  # Receiver mode
        while True:
            # print("Resetting loop")
            self.var = 0
            time.sleep(0.01)
            # self.reset_ptr_rx()
            # self.set_mode(MODE.RXCONT)  # Receiver mode


lora = mylora()
lora.set_sync_word(0x68)
# args = parser.parse_args(lora) # configs in LoRaArgumentParser.py

#     Slow+long range  Bw = 125 kHz, Cr = 4/8, Sf = 4096chips/symbol, CRC on. 13 dBm
lora.set_pa_config(pa_select=1, max_power=21, output_power=20)
lora.set_bw(BW.BW500)
lora.set_coding_rate(CODING_RATE.CR4_5)
lora.set_spreading_factor(8)
lora.set_rx_crc(True)
# lora.set_lna_gain(GAIN.G1)
lora.set_implicit_header_mode(False)
lora.set_low_data_rate_optim(False)

lora.set_pa_dac(1)
lora.set_ocp_trim(140)

#  Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on 13 dBm
# lora.set_pa_config(pa_select=1)


assert (lora.get_agc_auto_on() == 1)

try:
    print("START")
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("Exit")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("Exit")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()




# REG_OP_MODE = 0x01  # Register for operating mode
#
# # Switch to FSK mode: clear LoRa bit (MSB) by writing a value with bit 7 = 0.
# # Start by putting the module in sleep mode.
# lora.set_register(REG_OP_MODE, 0x00)  # FSK mode, sleep
# time.sleep(0.1)  # A little nap to let it settle
#
# # Now, set it to standby (still in FSK mode)
# lora.set_register(REG_OP_MODE, 0x01)  # FSK mode, standby