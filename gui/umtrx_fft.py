#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: UmTRX FFT
# Author: Fairwaves LLC
# Description: UmTRX FFT Waveform Plotter
# Generated: Mon Jan 28 11:50:15 2013
##################################################

from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from gnuradio.wxgui import scopesink2
from gnuradio.wxgui import waterfallsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import numpy
import wx

import sys
sys.path.append('../python_lib')

import umtrx_ctrl
import umtrx_lms
import lms_ctrl_panel

def create_umtrx_lms(lms_num, ip_address, bcast_addr):
        umtrx_lms_dev = umtrx_ctrl.create_umtrx_lms_device(lms_num, ip_address=ip_address, bcast_addr=bcast_addr)
        if umtrx_lms_dev is None: # UmTRX is not found
            print "UmTRX is not found"
            sys.exit(1)

        # Initialize and calibrate UmTRX
        umtrx_lms.lms_init(umtrx_lms_dev)
        umtrx_lms.lms_rx_enable(umtrx_lms_dev)
        umtrx_lms.lms_tx_enable(umtrx_lms_dev)
        # 0x0f - 0.75MHz
        lpf_bw_code = 0x0f
        pll_ref_clock = 26e6
        umtrx_lms.lms_auto_calibration(umtrx_lms_dev, int(pll_ref_clock), int(lpf_bw_code))
        umtrx_lms.lms_rx_disable(umtrx_lms_dev)
        umtrx_lms.lms_tx_disable(umtrx_lms_dev)

        return umtrx_lms_dev


class umtrx_fft_blank(grc_wxgui.top_block_gui):

	def __init__(self, address="", samp_rate=1e6, freq=935e6, gain=15, channel_num=0, antenna="RX1", bcast_addr="192.168.10.255", fft_size=1024, refresh_rate=30):
		grc_wxgui.top_block_gui.__init__(self, title="UmTRX FFT")

		##################################################
		# Parameters
		##################################################
		self.address = address
		self.samp_rate = samp_rate
		self.freq = freq
		self.gain = gain
		self.channel_num = channel_num
		self.antenna = antenna
		self.bcast_addr = bcast_addr
		self.fft_size = fft_size
		self.refresh_rate = refresh_rate

		##################################################
		# Variables
		##################################################
		self.var_samp_rate = var_samp_rate = samp_rate
		self.var_freq = var_freq = freq
		self.subdev = subdev = "A:0" if channel_num == 0 else "B:0"

		##################################################
		# UmTRX LMS
		##################################################
		self.umtrx_lms_dev = create_umtrx_lms(channel_num+1,
		                                      ip_address=address if address!="" else None,
		                                      bcast_addr=bcast_addr)

		##################################################
		# Blocks
		##################################################
		self._var_samp_rate_text_box = forms.text_box(
			parent=self.GetWin(),
			value=self.var_samp_rate,
			callback=self.set_var_samp_rate,
			label="Sample Rate",
			converter=forms.float_converter(),
		)
		self.GridAdd(self._var_samp_rate_text_box, 1, 0, 1, 1)
		_var_freq_sizer = wx.BoxSizer(wx.VERTICAL)
		self._var_freq_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_var_freq_sizer,
			value=self.var_freq,
			callback=self.set_var_freq,
			label="RX Tune Frequency",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._var_freq_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_var_freq_sizer,
			value=self.var_freq,
			callback=self.set_var_freq,
			minimum=300e6,
			maximum=3e9,
			num_steps=1000,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_var_freq_sizer, 1, 1, 1, 7)
		self.nb0 = self.nb0 = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
		self.nb0.AddPage(grc_wxgui.Panel(self.nb0), "FFT")
		self.nb0.AddPage(grc_wxgui.Panel(self.nb0), "Waterfall")
		self.nb0.AddPage(grc_wxgui.Panel(self.nb0), "Scope")
		self.GridAdd(self.nb0, 0, 0, 1, 8)
		self.wxgui_waterfallsink2_0 = waterfallsink2.waterfall_sink_c(
			self.nb0.GetPage(1).GetWin(),
			baseband_freq=0,
			dynamic_range=100,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=fft_size,
			fft_rate=refresh_rate,
			average=False,
			avg_alpha=None,
			title="Waterfall Plot",
			size=((-1, 400)),
		)
		self.nb0.GetPage(1).Add(self.wxgui_waterfallsink2_0.win)
		self.wxgui_scopesink2_0 = scopesink2.scope_sink_c(
			self.nb0.GetPage(2).GetWin(),
			title="Scope Plot",
			sample_rate=samp_rate,
			v_scale=0,
			v_offset=0,
			t_scale=0,
			ac_couple=False,
			xy_mode=False,
			num_inputs=1,
			trig_mode=gr.gr_TRIG_MODE_AUTO,
			y_axis_label="Counts",
		)
		self.nb0.GetPage(2).Add(self.wxgui_scopesink2_0.win)
		self.uhd_usrp_source_0 = uhd.usrp_source(
			device_addr=address,
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_source_0.set_subdev_spec(subdev, 0)
		self.uhd_usrp_source_0.set_samp_rate(var_samp_rate)
		self.uhd_usrp_source_0.set_center_freq(var_freq, 0)
		self.uhd_usrp_source_0.set_gain(gain, 0)
		self.uhd_usrp_source_0.set_antenna(antenna, 0)
		self.uhd_usrp_source_0.set_bandwidth(samp_rate, 0)
		self.fft = fftsink2.fft_sink_c(
			self.nb0.GetPage(0).GetWin(),
			baseband_freq=var_freq,
			y_per_div=10,
			y_divs=15,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=fft_size,
			fft_rate=refresh_rate,
			average=False,
			avg_alpha=None,
			title="FFT Plot",
			peak_hold=False,
			size=((-1, 400)),
		)
		self.nb0.GetPage(0).Add(self.fft.win)
		# Finally add the LMS control panel.
		# This should be done at the very end, because it should read LMS configuration values after UHD set it.
		self._lms_panel = lms_ctrl_panel.lms_ctrl_panel(parent=self.GetWin(), lms_iface=self.umtrx_lms_dev)
		self.GridAdd(self._lms_panel, 3, 0, 1, 8)

		##################################################
		# Connections
		##################################################
		self.connect((self.uhd_usrp_source_0, 0), (self.wxgui_scopesink2_0, 0))
		self.connect((self.uhd_usrp_source_0, 0), (self.wxgui_waterfallsink2_0, 0))
		self.connect((self.uhd_usrp_source_0, 0), (self.fft, 0))


	def get_address(self):
		return self.address

	def set_address(self, address):
		self.address = address

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.wxgui_scopesink2_0.set_sample_rate(self.samp_rate)
		self.set_var_samp_rate(self.samp_rate)
		self.uhd_usrp_source_0.set_bandwidth(self.samp_rate, 0)
		self.fft.set_sample_rate(self.samp_rate)
		self.wxgui_waterfallsink2_0.set_sample_rate(self.samp_rate)

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.set_var_freq(self.freq)

	def get_gain(self):
		return self.gain

	def set_gain(self, gain):
		self.gain = gain
		self.uhd_usrp_source_0.set_gain(self.gain, 0)

	def get_channel_num(self):
		return self.channel_num

	def set_channel_num(self, channel_num):
		self.channel_num = channel_num
		self.set_subdev("A:0" if self.channel_num == 0 else "B:0")

	def get_antenna(self):
		return self.antenna

	def set_antenna(self, antenna):
		self.antenna = antenna
		self.uhd_usrp_source_0.set_antenna(self.antenna, 0)

	def get_bcast_addr(self):
		return self.bcast_addr

	def set_bcast_addr(self, bcast_addr):
		self.bcast_addr = bcast_addr

	def get_fft_size(self):
		return self.fft_size

	def set_fft_size(self, fft_size):
		self.fft_size = fft_size

	def get_refresh_rate(self):
		return self.refresh_rate

	def set_refresh_rate(self, refresh_rate):
		self.refresh_rate = refresh_rate

	def get_var_samp_rate(self):
		return self.var_samp_rate

	def set_var_samp_rate(self, var_samp_rate):
		self.var_samp_rate = var_samp_rate
		self._var_samp_rate_text_box.set_value(self.var_samp_rate)
		self.uhd_usrp_source_0.set_samp_rate(self.var_samp_rate)

	def get_var_freq(self):
		return self.var_freq

	def set_var_freq(self, var_freq):
		self.var_freq = var_freq
		self._var_freq_slider.set_value(self.var_freq)
		self._var_freq_text_box.set_value(self.var_freq)
		self.uhd_usrp_source_0.set_center_freq(self.var_freq, 0)
		self.fft.set_baseband_freq(self.var_freq)

	def get_subdev(self):
		return self.subdev

	def set_subdev(self, subdev):
		self.subdev = subdev

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	parser.add_option("-a", "--address", dest="address", type="string", default="",
		help="Set IP address [default=%default]")
	parser.add_option("-r", "--samp-rate", dest="samp_rate", type="eng_float", default=eng_notation.num_to_str(1e6),
		help="Set sample rate [default=%default]")
	parser.add_option("-f", "--freq", dest="freq", type="eng_float", default=eng_notation.num_to_str(935e6),
		help="Set frequency [default=%default]")
	parser.add_option("-g", "--gain", dest="gain", type="eng_float", default=eng_notation.num_to_str(15),
		help="Set gain [default=%default]")
	parser.add_option("-c", "--channel-num", dest="channel_num", type="intx", default=0,
		help="Set UmTRX channel number [default=%default]")
	parser.add_option("-A", "--antenna", dest="antenna", type="string", default="RX1",
		help="Set RX1 [default=%default]")
	parser.add_option("-b", "--bcast-addr", dest="bcast_addr", type="string", default="192.168.10.255",
		help="Set UmTRX broadcast IP address [default=%default]")
	parser.add_option("", "--fft-size", dest="fft_size", type="intx", default=1024,
		help="Set FFT size [default=%default]")
	parser.add_option("", "--refresh-rate", dest="refresh_rate", type="intx", default=30,
		help="Set FFT refresh rate [default=%default]")
	(options, args) = parser.parse_args()
	tb = umtrx_fft_blank(address=options.address, samp_rate=options.samp_rate, freq=options.freq, gain=options.gain, channel_num=options.channel_num, antenna=options.antenna, bcast_addr=options.bcast_addr, fft_size=options.fft_size, refresh_rate=options.refresh_rate)
	tb.Run(True)

