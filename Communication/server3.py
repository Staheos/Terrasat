#!/usr/bin/env python3

""" This program asks a client for data and waits for the response, then sends an ACK. """

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
        BOARD.led_on()
        print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        recv_hash = hashlib.sha1(bytes(payload)).hexdigest()
        print(f"Recv payload: {recv_hash}   {payload}")
        print(bytes(payload).decode("utf-8", 'ignore'))  # Receive DATA
        BOARD.led_off()
        time.sleep(1)  # Wait for the client be ready
        try:
            ack = {
                "type": "ACK",
                "hash": recv_hash,
                "sig": "TERRASAT"
            }
            ack_payload = get_message_bytes(frame(json.dumps(ack)))
            # self.write_payload([255, 255, 0, 0, 65, 67, 75, 0])  # Send ACK
            print("Sending ACK: " + str(ack["hash"]))
            print("Sent ACK: " + str(self.write_payload(ack_payload)))
            self.set_mode(MODE.TX)
        except Exception as e:
            print(f"ACK Error: {e}")
        time.sleep(0.5)
        self.var = 1

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
        while True:
            while (self.var == 0):
                try:
                    # print("Send SYN")
                    syn = {
                        "type": "SYN",
                        "sig": "TERRASAT",
                        "data": "ANY"
                    }
                    print("Sent payload: " + str(self.write_payload(get_message_bytes("INF"))))
                    syn_payload = get_message_bytes(frame(json.dumps(syn)))
                    # print("Sending payload: " + str(syn_payload))
                    # payload = [255, 255, 0, 0, 73, 78, 70, 0]
                    # print("Sending payload: " + str(payload))
                    # print("Sent payload: " + str(self.write_payload(syn_payload)))
                    self.set_mode(MODE.TX)
                    # wait for data request to be sent
                    time.sleep(0.2)  # there must be a better solution but sleep() works
                except Exception as e:
                    print(f"SYN Error: {e}")

                self.reset_ptr_rx()
                self.set_mode(MODE.RXCONT)  # Receiver mode

                start_time = time.time()
                while (time.time() - start_time < 4):  # wait until receive data or 3s
                    pass;

            print("Resetting loop")
            self.var = 0
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)  # Receiver mode
            time.sleep(0.5)


lora = mylora()
lora.set_sync_word(0x68)
# args = parser.parse_args(lora) # configs in LoRaArgumentParser.py

#     Slow+long range  Bw = 125 kHz, Cr = 4/8, Sf = 4096chips/symbol, CRC on. 13 dBm
lora.set_pa_config(pa_select=1, max_power=21, output_power=20)
lora.set_bw(BW.BW500)
lora.set_coding_rate(CODING_RATE.CR4_7)
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