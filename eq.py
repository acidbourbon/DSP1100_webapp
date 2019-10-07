#!/usr/bin/env python3

from flask import Flask, jsonify, render_template, request
import time
#import numpy as np

import mido

class behringer_eq:
  output = None
  filter_chan = -1
  freq_lookup = {
      20:0,
      25:1,
      32:2,
      40:3,
      60:4,
      63:5,
      80:6,
      100:7,
      125:8,
      160:9,
      200:10,
      250:11,
      320:12,
      400:13,
      500:14,
      630:15,
      800:16,
      1000:17,
      1250:18,
      1600:19,
      2000:20,
      2500:21,
      3200:22,
      4000:23,
      5000:24,
      6300:25,
      8000:26,
      10000:27,
      12500:28,
      16000:29,
      20000:30
  }
  
  bandwidth_mem = {}
  freq_mem      = {}
  
  def __init__(self):
    self.output = mido.open_output('CH345 MIDI 1') # this is the logilink midi thing
    
  def set_gain(self,filter_chan,gain):
    self.select_filter_chan(filter_chan)
    # set gain for current filter : value = 0-64
    # value 48 is +0dB, value 48+x is +x dB, 48-x is -x dB, it is that easy
    self.output.send(mido.Message('control_change', control=16, value=gain+48))
    
  def set_bandwidth(self,filter_chan,bandwidth):
    
    if filter_chan in self.bandwidth_mem:
      if self.bandwidth_mem[filter_chan] == bandwidth:
        return
    
    self.select_filter_chan(filter_chan)
    # value is in 1/60 octaves, argument bandwith is given in octaves
    self.output.send(mido.Message('control_change', control=15, value=int(bandwidth*60.)))
    self.bandwidth_mem[filter_chan] = bandwidth
    
  def set_freq(self,filter_chan,freq):
      
    if filter_chan in self.freq_mem:
      if self.freq_mem[filter_chan] == freq:
        return
    
    self.select_filter_chan(filter_chan)
    self.output.send(mido.Message('control_change', control=13, value=int(self.freq_lookup[int(freq)])))
    self.freq_mem[filter_chan] = freq
    

  def select_filter_chan(self,filter_chan):
    # select filter : value = 0-11
    if(filter_chan != self.filter_chan): ## only send if different channel is selected
      self.output.send(mido.Message('control_change', control=10, value=filter_chan))
      self.filter_chan = filter_chan
    

my_eq = behringer_eq()

app = Flask(__name__)

@app.route('/')
def index():
    #return 'Hello world'
    return render_template('eq.html') # has to be located in ./templates/

@app.route('/set_eq')
def set_eq():
    a = int(request.args.get('a', 0))
    freq = int(request.args.get('freq', 500))
    bandwidth = float(request.args.get('bandwidth', 0.66))
    filter_chan = int(request.args.get('filter_chan', 0))
    gain = int(request.args.get('gain', 0))
    
    print("received a={:d}".format(a))
    #b = int(request.args.get('b', 0))
    #div = 'na'
    #if b != 0:
        #div = a/b
    #my_eq.set_gain(0,a)
    time.sleep(0.02)
    my_eq.set_freq(filter_chan,freq)
    my_eq.set_bandwidth(filter_chan,bandwidth)
    my_eq.set_gain(filter_chan,gain)
    
    return jsonify({
        #"a"        :  a,
        #"b"        :  b,
        #"add"      :  a+b,
        #"multiply" :  a*b,
        #"subtract" :  a-b,
        #"divide"   :  div,
        "dummy" : 0
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
