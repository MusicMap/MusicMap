#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import numpy as np
import scipy.io.wavfile as wav


class WavFile:
    def __init__(self, file_name, scale=False):
        r"""
        :param file_name: Input file name for "*.wav"

        :param scale: Scale track values in [-1, 1]
        """
        self.file_name = file_name
        self.rate, self.samples = wav.read(file_name)

        if len(self.samples.shape) == 1:
            self.samples.reshape((len(self.samples), 1))
        elif len(self.samples.shape) != 2:
            raise Exception("Wrong file format!")

        if scale:
            nb_bits = re.findall(r"int(\d+)", str(self.samples.dtype))
            if len(nb_bits) > 0:
                nb_bits = int(nb_bits[0])
                self.samples = np.divide(self.samples, 2.0 ** nb_bits)
            else:
                raise Exception("Wrong file format!")

    def __len__(self):
        r"""
        :return: track's length in seconds
        """
        return self.samples.shape[0] / self.rate

    def get_channels(self):
        r"""
        Number of channels in track. Usually equals 2 (left and right ears).

        :return: nb_channels
        """
        return self.samples.shape[1]

    def get_sub_track(self, start_sec=None, end_sec=None, channel=0):
        r"""
        :param start_sec: start position in seconds. if None, treat as start_sec = 0 seconds

        :param end_sec: finish position in seconds. if None, treat as end_sec = end_of_track in seconds

        :param channel: channel (usually 0 or 1)

        :return: part of track's channel, starting form start_sec and finishing end_sec
        """
        if start_sec is not None and end_sec is not None and start_sec >= end_sec:
            raise Exception("Start should be less then end")

        l_border = 0 if start_sec is None else start_sec * self.rate
        r_border = len(self) if end_sec is None else end_sec * self.rate
        return self.samples[l_border:r_border, channel]

    def split(self, part_time):
        """
        :param part_time: count of second in each part
        """
        l_border = 0
        r_border = len(self) * self.rate
        print r_border, part_time * self.rate
        print self.samples.shape
        part_begin = 0
        idx = 0
        # print self.get_channels()
        while part_begin + part_time * self.rate <= r_border:
            wav.write(self.file_name[:-4] + "_" + str(idx) + self.file_name[-4:], self.rate, \
                      self.samples[part_begin:part_begin + part_time * self.rate])
            print idx
            print self.samples[part_begin:part_begin + part_time * self.rate].shape
            idx += 1
            part_begin += part_time * self.rate


if __name__ == "__main__":
    pass
