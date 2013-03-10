#!/bin/sh

UMTRX_IP=192.168.10.2

if [ $# -ne 1 -o ! \( "x$1" = "x1" -o "x$1" = "x2" \) ] ; then
    echo
    echo "Script for UmTRX LMS SPI testing."
    echo
    echo "Usage: $0 <channel-num>"
    echo
    echo "      channel-num - channel number on UmTRX [1;2]"
    exit 1
fi

LMS_NUM=$1

send_lms_cmd()
{
#    echo "\n\n---------------------- $* ----------------------"
#    read t
    ../python_lib/umtrx_lms.py --umtrx-addr=$UMTRX_IP --lms $LMS_NUM $*
}

send_lms_cmd --lms-init
send_lms_cmd --lms-tx-enable 1
send_lms_cmd --lms-rx-enable 1
# -10dB is a good value for calibration if don't know a target gain yet
send_lms_cmd --lms-set-tx-vga1-gain -10
send_lms_cmd --pll-ref-clock 26e6 --lpf-bandwidth-code 0x0f --lms-auto-calibration

# Set Rx and Tx LPF to 0.75MHz
send_lms_cmd --reg 0x34 --data 0x3e
send_lms_cmd --reg 0x54 --data 0x3e

# Tx side
send_lms_cmd --lms-tx-pll-tune 945.6e6
send_lms_cmd --lms-set-tx-vga1-gain -10
send_lms_cmd --lms-set-tx-vga2-gain 15
send_lms_cmd --lms-set-tx-pa 2
#send_lms_cmd --lms-set-tx-pa 0

# Rx side
send_lms_cmd --lms-rx-pll-tune 900.2e6
send_lms_cmd --lms-set-rx-vga2-gain 9
#send_lms_cmd --lms-set-rx-lna 1

# Calibration
#send_lms_cmd --reg 0x42 --data 0x72
#send_lms_cmd --reg 0x43 --data 0x8A

