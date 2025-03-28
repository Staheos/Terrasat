#!/usr/bin/env python3

""" This program sends a response whenever it receives the "INF" """
import queue
# Copyright 2018 Rui Silva.
#
# This file is part of rpsreal/pySX127x, fork of mayeranalytics/pySX127x.

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
    def __init__(self, packet_queue: queue.Queue, verbose=is_debug()):
        super(mylora, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0, 0, 0, 0, 0, 0])
        self.var = 0
        self.packet_queue = packet_queue

    def on_rx_done(self):
        log("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)  # Receive INF
        log(f"Recv payload: {payload}")
        mens = bytes(payload).decode("utf-8", 'ignore')
        mens = mens[2:-1]  # to discard \x00\x00 and \x00 at the end
        log(mens)
        BOARD.led_off()
        if mens == "INF":
            log("Received data request INF")
            # time.sleep(0.05)
            packet = ""
            for _ in range(0, 10):
                if self.packet_queue.empty():
                    break
                packet += self.packet_queue.get(block=True, timeout=1)
                if len(packet.encode()) > 155:
                    break
            if packet == "":
                packet = "NODATA"
            else:
                self.packet_queue.task_done()
            # packet += "\r\n"
            log("Sending: " + str(packet))
            sending_payload = get_message_bytes(packet)
            log("Sending payload: " + str(sending_payload))
            # sending_payload = [255, 255, 0, 0, 68, 65, 84, 65, 32, 82, 65, 83, 80, 66, 69, 82, 82, 89, 32, 80, 73, 0]
            # log("Sending payload: " + str(sending_payload))
            log("Sent payload: " + str(self.write_payload(sending_payload)))
            self.set_mode(MODE.TX)
        elif mens == "ACK":
            log("Received ACK")
        time.sleep(0.3)
        self.var = 1

    def on_tx_done(self):
        log("\nTxDone")
        log(self.get_irq_flags())

    def on_cad_done(self):
        log("\non_CadDone")
        log(self.get_irq_flags())
        self.var = 1

    def on_rx_timeout(self):
        log("\non_RxTimeout")
        log(self.get_irq_flags())
        self.var = 1

    def on_valid_header(self):
        log("\non_ValidHeader")
        log(self.get_irq_flags())

    def on_payload_crc_error(self):
        log("\non_PayloadCrcError")
        log(self.get_irq_flags())

    def on_fhss_change_channel(self):
        log("\non_FhssChangeChannel")
        log(self.get_irq_flags())

    def start(self):
        while True:
            self.var = 0
            while self.var == 0:
                log("Sending data loop")
                packet = ""
                new_packet = ""
                while len(packet.encode("utf-8", errors="strict")) + len(new_packet.encode("utf-8", errors="strict")) < 150:
                    packet += new_packet
                    new_packet = ""
                    if self.packet_queue.empty():
                        break
                    new_packet = self.packet_queue.get(block=True, timeout=1)

                if new_packet != "":
                    self.packet_queue.put(new_packet)

                if packet == "":
                    packet = "NODATA"
                    time.sleep(0.15)
                    continue

                self.packet_queue.task_done()

                log("Sending: " + str(packet))
                sending_payload = get_message_bytes(packet)
                log("Sending payload: " + str(sending_payload))
                log("Sent payload: " + str(self.write_payload(sending_payload)))
                self.set_dio_mapping([1, 0, 0, 0, 0, 0])
                self.set_mode(MODE.TX)
                while self.get_mode() == MODE.TX:
                    time.sleep(0.01)
                log("Changed to mode: " + str(self.get_mode()))
                self.set_dio_mapping([0, 0, 0, 0, 0, 0])
                time.sleep(0.1)

            log("Resetting loop")
            assert (self.get_agc_auto_on() == 1)
