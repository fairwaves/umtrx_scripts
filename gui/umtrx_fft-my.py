#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: UmTRX FFT
# Author: Fairwaves LLC
# Description: UmTRX FFT Waveform Plotter
# Generated: Sun Jan 27 20:16:37 2013
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
import umtrx_ctrl
import umtrx_lms
import lms_ctrl_panel

def create_umtrx_lms(lms_num):
        umtrx_lms_dev = umtrx_ctrl.create_umtrx_lms_device(lms_num)
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


class uhd_fft(grc_wxgui.top_block_gui):

	def __init__(self, param_freq=935e6, param_gain=15, param_samp_rate=1e6, address="", param_antenna="RX1", param_bcast_addr="192.168.10.255", param_channel_num=0):
		grc_wxgui.top_block_gui.__init__(self, title="UmTRX FFT")

		##################################################
		# Parameters
		##################################################
		self.param_freq = param_freq
		self.param_gain = param_gain
		self.param_samp_rate = param_samp_rate
		self.address = address
		self.param_antenna = param_antenna
		self.param_bcast_addr = param_bcast_addr
		self.param_channel_num = param_channel_num

		##################################################
		# Variables
		##################################################
		self.subdev = subdev = "A:0" if param_channel_num == 0 else "B:0"
		self.samp_rate = samp_rate = param_samp_rate
		self.gain = gain = param_gain
		self.freq = freq = param_freq

		##################################################
		# UmTRX LMS
		##################################################
		self.umtrx_lms_dev = create_umtrx_lms(param_channel_num+1)

		##################################################
		# Blocks
		##################################################
		self._samp_rate_text_box = forms.text_box(
			parent=self.GetWin(),
			value=self.samp_rate,
			callback=self.set_samp_rate,
			label="Sample Rate",
			converter=forms.float_converter(),
		)
		self.GridAdd(self._samp_rate_text_box, 1, 0, 1, 3)
		self.nb0 = self.nb0 = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
		self.nb0.AddPage(grc_wxgui.Panel(self.nb0), "FFT")
		self.nb0.AddPage(grc_wxgui.Panel(self.nb0), "Waterfall")
		self.nb0.AddPage(grc_wxgui.Panel(self.nb0), "Scope")
		self.GridAdd(self.nb0, 0, 0, 1, 8)
		self._lms_panel = lms_ctrl_panel.lms_ctrl_panel(parent=self.GetWin(), lms_iface=self.umtrx_lms_dev)
		self.GridAdd(self._lms_panel, 3, 0, 1, 8)
		_freq_sizer = wx.BoxSizer(wx.VERTICAL)
		self._freq_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_freq_sizer,
			value=self.freq,
			callback=self.set_freq,
			label="RX Tune Frequency",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._freq_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_freq_sizer,
			value=self.freq,
			callback=self.set_freq,
			minimum=300e6,
			maximum=3e9,
			num_steps=1000,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_freq_sizer, 1, 3, 1, 5)
		self.wxgui_waterfallsink2_0 = waterfallsink2.waterfall_sink_c(
			self.nb0.GetPage(1).GetWin(),
			baseband_freq=0,
			dynamic_range=100,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=512,
			fft_rate=15,
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
		self.uhd_usrp_source_0.set_samp_rate(samp_rate)
		self.uhd_usrp_source_0.set_center_freq(freq, 0)
		self.uhd_usrp_source_0.set_gain(gain, 0)
		self.uhd_usrp_source_0.set_antenna("RX1", 0)
		self.uhd_usrp_source_0.set_bandwidth(samp_rate, 0)
		self.fft = fftsink2.fft_sink_c(
			self.nb0.GetPage(0).GetWin(),
			baseband_freq=freq,
			y_per_div=10,
			y_divs=15,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=1024,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="FFT Plot",
			peak_hold=False,
			size=((-1, 400)),
		)
		self.nb0.GetPage(0).Add(self.fft.win)

		##################################################
		# Connections
		##################################################
		self.connect((self.uhd_usrp_source_0, 0), (self.wxgui_scopesink2_0, 0))
		self.connect((self.uhd_usrp_source_0, 0), (self.wxgui_waterfallsink2_0, 0))
		self.connect((self.uhd_usrp_source_0, 0), (self.fft, 0))


	def get_param_freq(self):
		return self.param_freq

	def set_param_freq(self, param_freq):
		self.param_freq = param_freq
		self.set_freq(self.param_freq)

	def get_param_gain(self):
		return self.param_gain

	def set_param_gain(self, param_gain):
		self.param_gain = param_gain
		self.set_gain(self.param_gain)

	def get_param_samp_rate(self):
		return self.param_samp_rate

	def set_param_samp_rate(self, param_samp_rate):
		self.param_samp_rate = param_samp_rate
		self.set_samp_rate(self.param_samp_rate)

	def get_address(self):
		return self.address

	def set_address(self, address):
		self.address = address

	def get_param_antenna(self):
		return self.param_antenna

	def set_param_antenna(self, param_antenna):
		self.param_antenna = param_antenna

	def get_param_bcast_addr(self):
		return self.param_bcast_addr

	def set_param_bcast_addr(self, param_bcast_addr):
		self.param_bcast_addr = param_bcast_addr

	def get_param_channel_num(self):
		return self.param_channel_num

	def set_param_channel_num(self, param_channel_num):
		self.param_channel_num = param_channel_num
		self.set_subdev("A:0" if self.param_channel_num == 0 else "B:0")

	def get_subdev(self):
		return self.subdev

	def set_subdev(self, subdev):
		self.subdev = subdev

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.wxgui_scopesink2_0.set_sample_rate(self.samp_rate)
		self.fft.set_sample_rate(self.samp_rate)
		self._samp_rate_text_box.set_value(self.samp_rate)
		self.wxgui_waterfallsink2_0.set_sample_rate(self.samp_rate)
		self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
		self.uhd_usrp_source_0.set_bandwidth(self.samp_rate, 0)

	def get_gain(self):
		return self.gain

	def set_gain(self, gain):
		self.gain = gain
		self._gain_slider.set_value(self.gain)
		self._gain_text_box.set_value(self.gain)
		self.uhd_usrp_source_0.set_gain(self.gain, 0)

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.fft.set_baseband_freq(self.freq)
		self._freq_slider.set_value(self.freq)
		self._freq_text_box.set_value(self.freq)
		self.uhd_usrp_source_0.set_center_freq(self.freq, 0)

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	parser.add_option("-f", "--param-freq", dest="param_freq", type="eng_float", default=eng_notation.num_to_str(935e6),
		help="Set frequency [default=%default]")
	parser.add_option("-g", "--param-gain", dest="param_gain", type="eng_float", default=eng_notation.num_to_str(15),
		help="Set gain [default=%default]")
	parser.add_option("-r", "--param-samp-rate", dest="param_samp_rate", type="eng_float", default=eng_notation.num_to_str(1e6),
		help="Set sample rate [default=%default]")
	parser.add_option("-a", "--address", dest="address", type="string", default="",
		help="Set IP address [default=%default]")
	parser.add_option("-A", "--param-antenna", dest="param_antenna", type="string", default="RX1",
		help="Set antenna [default=%default]")
	parser.add_option("-b", "--param-bcast-addr", dest="param_bcast_addr", type="string", default="192.168.10.255",
		help="Set UmTRX broadcast IP address [default=%default]")
	parser.add_option("-c", "--param-channel-num", dest="param_channel_num", type="intx", default=0,
		help="Set UmTRX channel number [default=%default]")
	(options, args) = parser.parse_args()
	tb = uhd_fft(param_freq=options.param_freq, param_gain=options.param_gain, param_samp_rate=options.param_samp_rate, address=options.address, param_antenna=options.param_antenna, param_bcast_addr=options.param_bcast_addr, param_channel_num=options.param_channel_num)
	tb.Run(True)

