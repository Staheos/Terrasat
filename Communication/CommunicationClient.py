import threading
import sys
import socket
import queue
import time
from client0 import *
from SX127x.constants import MODE, BW, CODING_RATE

class CommunicationClient(threading.Thread):
    def __init__(self, stopq: queue.Queue, packet_queue: queue.Queue):
        threading.Thread.__init__(self, args=(), kwargs={})
        self.stopq = stopq
        self.packet_queue = packet_queue
        # self.daemon = True
        self.received = bytearray()
        self.lora = mylora(packet_queue)

    def run(self) -> None:
        print("CommunicationClient started")
        # args = parser.parse_args(lora) # configs in LoRaArgumentParser.py

        #     Slow+long range  Bw = 125 kHz, Cr = 4/8, Sf = 4096chips/symbol, CRC on. 13 dBm
        self.lora.set_sync_word(0x68)
        self.lora.set_pa_config(pa_select=1, max_power=21, output_power=20)
        self.lora.set_bw(BW.BW500)
        self.lora.set_coding_rate(CODING_RATE.CR4_7)
        self.lora.set_spreading_factor(8)
        self.lora.set_rx_crc(True)
        # self.lora.set_lna_gain(GAIN.G1)
        self.lora.set_implicit_header_mode(False)
        self.lora.set_low_data_rate_optim(False)

        self.lora.set_pa_dac(1)
        self.lora.set_ocp_trim(140)

        #  Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on 13 dBm
        # self.lora.set_pa_config(pa_select=1)

        assert (self.lora.get_agc_auto_on() == 1)

        try:
            print("START")
            self.lora.start()
        except KeyboardInterrupt:
            sys.stdout.flush()
            print("Exit")
            sys.stderr.write("KeyboardInterrupt\n")
        finally:
            sys.stdout.flush()
            print("Exit")
            self.lora.set_mode(MODE.SLEEP)
            BOARD.teardown()

        print("CommunicationClient finished")