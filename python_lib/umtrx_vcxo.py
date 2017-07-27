#!/usr/bin/env python
#
# Copyright 2012 Sylvain Munaut <tnt@246tNt.com>
# Copyright 2012-2017 Alexander Chemeris <Alexander.Chemeris@fairwaves.co>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import socket, argparse, time
import umtrx_ctrl

description = """ UmTRX VCTCXO control tool.
When run without any command line parameters, it reads various information from UmTRX and print it to screen.
When run with command line parameters, specified actions are applied as well.
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = description,
        epilog = "UmTRX is detected via broadcast unless explicit address is specified via --umtrx-addr option. 'None' returned while reading\writing indicates error in the process.")
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    basic_opt = parser.add_mutually_exclusive_group()
    basic_opt.add_argument('--detect', dest = 'bcast_addr', default = '192.168.10.255', help='broadcast domain where UmTRX should be discovered (default: 192.168.10.255)')
    basic_opt.add_argument('--umtrx-addr', dest = 'umtrx', const = '192.168.10.2', nargs='?', help = 'UmTRX address (default: 192.168.10.2)')

    parser.add_argument('--dac-value', dest = 'dac', type = int, help = 'Set VCTCXO DAC to this value (12 bit)')
    parser.add_argument('--gpsdo-debug', dest = 'gpsdo_debug', type = int, help = 'Enable/disable GPSDO debug')

    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(umtrx_ctrl.UDP_TIMEOUT)
    umtrx = umtrx_ctrl.detect(sock, args.umtrx if args.umtrx is not None else args.bcast_addr)

    if umtrx is not None: # UmTRX address established
        if umtrx_ctrl.ping(sock, umtrx): # UmTRX probed
            print('UmTRX detected at %s' % umtrx)
            umtrx_vcxo_dev = umtrx_ctrl.umtrx_vcxo_dac(sock, umtrx)
            if args.gpsdo_debug is not None:
                umtrx_vcxo_dev.set_gpsdo_debug(args.gpsdo_debug)
                print('Set GPSDO debug to: %s' % (str(args.gpsdo_debug),))
            print('Current DAC value: %d' % umtrx_vcxo_dev.get_dac())
            print('Current TCXO frequency (immediate): %d' % umtrx_vcxo_dev.get_gpsdo_freq())
            print('Current TCXO frequency (filtered):  %.3f' % (umtrx_vcxo_dev.get_gpsdo_freq_lpf()/8))
            if args.dac is not None:
                umtrx_vcxo_dev.set_dac(args.dac)
                print('Set DAC to value: %d' % umtrx_vcxo_dev.get_dac())
        else:
            print('UmTRX at %s is not responding.' % umtrx)
    else:
        print('No UmTRX detected over %s' % args.bcast_addr)
