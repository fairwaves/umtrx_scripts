#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <nbformat>2</nbformat>

# <codecell>

import wx
from grc_gnuradio import wxgui as grc_wxgui
from gnuradio.wxgui import forms, form
import umtrx_ctrl
import umtrx_lms

class lms_ctrl_panel(grc_wxgui.panel.Panel):
    def __init__(self, parent, lms_iface, orient=wx.VERTICAL):
        grc_wxgui.panel.Panel.__init__(self, parent, orient)
        # Save LMS interface object
        self.lms = lms_iface
        # Generate GUI
        self._generate_panel()

    def _generate_panel(self):
        # Rx LNA Selection
        self.rx_lna_chooser = forms.drop_down(
            parent=self.GetWin(),
            value=umtrx_lms.lms_get_rx_lna(self.lms),
            callback=self.set_rx_lna,
            label="Rx LNA",
            choices=[0, 1, 2, 3],
            labels=["Disabled","LNA1","LNA2", "LNA3"],
#            style=wx.RA_HORIZONTAL,
            )
        self.GridAdd(self.rx_lna_chooser, 0, 0, 1, 1)

        # Rx LNA Mode
        self.rx_lna_gain_mode_chooser = forms.drop_down(
            parent=self.GetWin(),
            value=umtrx_lms.lms_get_rx_lna_gain(self.lms),
            callback=self.set_rx_lna_gain_mode,
            label="Rx LNA Mode",
            choices=[3, 2, 1],
            labels=["3: Norm","3: -6dB","1: Bypass"],
#            style=wx.RA_HORIZONTAL,
            )
        self.GridAdd(self.rx_lna_gain_mode_chooser, 0, 1, 1, 1)

        # Rx LPF bandwidth
        self.rx_lna_gain_mode_chooser = forms.drop_down(
            parent=self.GetWin(),
            value=umtrx_lms.lms_get_rx_lpf_raw(self.lms),
            callback=self.set_rx_lpf,
            label="Rx LNA LPF",
            choices=[15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
            labels=[0.75, 0.875, 1.25, 1.375, 1.5, 1.92, 2.5, 2.75, 3, 3.5, 4.375, 5, 6, 7, 10, 14],
#            style=wx.RA_HORIZONTAL,
            )
        self.GridAdd(self.rx_lna_gain_mode_chooser, 0, 2, 1, 1)
        
        # Rx VGA1 gain
        self.rx_vga1gain = umtrx_lms.lms_get_rx_vga1gain_int(self.lms)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.rx_vga1gain_slider = form.slider_field(
            parent=self.GetWin(), sizer=hbox,
            value=self.rx_vga1gain,
            callback=self.set_rx_vga1gain,
            label="Rx VGA1 gain (raw)\n120=30dB, 102=19dB, 2=5dB",
            min=0, max=127,
            )
        self.GridAdd(hbox, 1, 0, 1, 8)
        
        # Rx VGA2 gain
        self.rx_vga2gain = umtrx_lms.lms_get_rx_vga2gain(self.lms)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.rx_vga2gain_slider = form.slider_field(
            parent=self.GetWin(), sizer=hbox,
            value=self.rx_vga2gain,
            callback=self.set_rx_vga2gain,
            label="\nRx VGA2 gain (dB)",
            min=0, max=30,# Not recommended to use above 30
            )
        self.GridAdd(hbox, 2, 0, 1, 8)
        
    def set_rx_lna(self, value):
        print "set_rx_lna(%d)" % (value)
        umtrx_lms.lms_set_rx_lna(self.lms, value)
        
    def set_rx_lna_gain_mode(self, value):
        print "set_rx_lna_gain_mode(%d)" % (value)
        umtrx_lms.lms_set_rx_lna_gain(self.lms, value)
        
    def set_rx_lpf(self, value):
        print "set_rx_lpf(%d)" % (value)
        umtrx_lms.lms_set_rx_lpf_raw(self.lms, value)
        
    def set_rx_vga1gain(self, value):
        # Don't set value twice
        if self.rx_vga2gain == value: return
        print "set_rx_vga1gain(%d)" % (value)
        # Set the value
        umtrx_lms.lms_set_rx_vga1gain_int(self.lms, value)
        # Read back the value
        self.rx_vga1gain = umtrx_lms.lms_get_rx_vga1gain_int(self.lms)
        self.rx_vga1gain_slider.set_value(self.rx_vga1gain)
        
    def set_rx_vga2gain(self, value):
        print "set_rx_vga2gain(%d)" % (value)
        # Rounding
        if value > self.rx_vga2gain: self.rx_vga2gain = ((value+2)/3)*3
        else: self.rx_vga2gain = ((value)/3)*3
        print "set_rx_vga2gain(%d) rounded=%d" % (value, self.rx_vga2gain)
        # Set the value
        umtrx_lms.lms_set_rx_vga2gain(self.lms, self.rx_vga2gain)
        # Read back the value
        self.rx_vga2gain = umtrx_lms.lms_get_rx_vga2gain(self.lms)
        self.rx_vga2gain_slider.set_value(self.rx_vga2gain)
        print "set_rx_vga2gain(%d) actual=%d" % (value, self.rx_vga2gain)
        

# <codecell>

# ----------------------------------------------------------------
#                    Stand-alone example code
# ----------------------------------------------------------------

import sys
from gnuradio.wxgui import stdgui2

class demo_app_flow_graph (stdgui2.std_top_block):
    def __init__(self, frame, panel, vbox, argv):
        stdgui2.std_top_block.__init__ (self, frame, panel, vbox, argv)

        self.frame = frame
        self.panel = panel

        def _print_kv(kv):
            print "kv =", kv
            return True

        self.lms_panel = lms_ctrl_panel(panel, umtrx_lms_dev)
        
        vbox.Add(self.lms_panel, 0, wx.CENTER)
        
    def _set_status_msg(self, msg):
        self.frame.GetStatusBar().SetStatusText(msg, 0)


def main ():
    app = stdgui2.stdapp(demo_app_flow_graph, "UmTRX control GUI", nstatus=1)
    app.MainLoop ()

if __name__ == '__main__':
    lms_num = 2
    umtrx_lms_dev = umtrx_ctrl.create_umtrx_lms_device(lms_num)
    if umtrx_lms_dev is None:
        # No UmTRX found
        import sys
        sys.exit(1)

    if 0:
        umtrx_lms.lms_init(umtrx_lms_dev)
        umtrx_lms.lms_rx_enable(umtrx_lms_dev)
        umtrx_lms.lms_tx_enable(umtrx_lms_dev)
        # 0x0f - 0.75MHz
        lpf_bw_code = 0x0f
        pll_ref_clock = 26e6
        umtrx_lms.lms_auto_calibration(umtrx_lms_dev, int(pll_ref_clock), int(lpf_bw_code))
        umtrx_lms.lms_rx_disable(umtrx_lms_dev)
        umtrx_lms.lms_tx_disable(umtrx_lms_dev)

    main ()

# <codecell>


