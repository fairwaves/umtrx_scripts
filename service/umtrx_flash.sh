#!/bin/sh

# Program UmTRX FPGA bitstream and ZPU firmware. Used by a factory.

######## CONFIGURATION START ########

# USE_JTAG - "yes" to use xc3sprog to load initial FPGA image.
#            "no" to skip this step.
USE_JTAG="no"

# IP_ADDR - IP address of UmTRX 
IP_ADDR="192.168.10.2"

# Paths to utils we need
XC3SPROG=./xc3sprog
USRP_BURN_MB_EEPROM=./usrp_burn_mb_eeprom
USRP_N2XX_NET_BURNER=./usrp_n2xx_net_burner.py

######### CONFIGURATION END #########


if [ $# -ne 1 ] ; then
    echo
    echo "Script for UmTRX flashing after manufacturing."
    echo
    echo "Usage: $0 <serial-number>"
    echo
    echo "      serial-number - UmTRX serial number"
    exit 1
fi

# Load values from command line and settings
SERNUM=$1

# Write FPGA bitstream over JTAG to RAM (skipping flash). It will work as a
# temporary bootloader for later flashing over Ethernet. We don't write
# directly to flash (with `-I` option), because it rarely works.
if [ "x$USE_JTAG" = "xyes" ] ; then
    sudo $XC3SPRO -c jtaghs1 u2plus_umtrx_v2.bit
fi

# Configure EEPROM to default values.
$USRP_BURN_MB_EEPROM --args addr=$IP_ADDR --key hardware --val 64000
$USRP_BURN_MB_EEPROM --args addr=$IP_ADDR --key serial   --val $SERNUM
$USRP_BURN_MB_EEPROM --args addr=$IP_ADDR --key name     --val UmTRX
$USRP_BURN_MB_EEPROM --args addr=$IP_ADDR --key mac-addr --val 00:50:c2:85:3f:ff
$USRP_BURN_MB_EEPROM --args addr=$IP_ADDR --key ip-addr  --val 192.168.10.2
$USRP_BURN_MB_EEPROM --args addr=$IP_ADDR --key tcxo-dac --val 2048

# Flash FPGA bitstream and ZPU firmware images to flash, over Ethernet.
$USRP_N2XX_NET_BURNER --addr=$IP_ADDR --fpga=u2plus_umtrx.bin --overwrite-safe
$USRP_N2XX_NET_BURNER --addr=$IP_ADDR --fpga=u2plus_umtrx.bin
$USRP_N2XX_NET_BURNER --addr=$IP_ADDR --fw=usrp2p_txrx_uhd.bin
