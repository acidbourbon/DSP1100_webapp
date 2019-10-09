#!/usr/bin/env python3

from flask import Flask, jsonify, render_template, request
import time
#import numpy as np

import mido
import numpy as np

class behringer_eq:
  output = None
  filter_chan = -1
  
  iso_freq_list = np.array([
        20,
        25,
        31.5,
        40,
        50,
        63,
        80,
        100,
        125,
        160,
        200,
        250,
        315,
        400,
        500,
        630,
        800,
        1000,
        1250,
        1600,
        2000,
        2500,
        3150,
        4000,
        5000,
        6300,
        8000,
        10000,
        12500,
        16000,
        20000
        ])


  def find_fine_freq(self,freq):
      
    if freq < 20:
      freq = 20
      
    if freq > 20000:
      freq = 20000
      
    index_floor = np.nonzero(iso_freq_list <= freq)[0][-1] # last index of iso_freq_list that is <= freq
    index_ceil  = index_floor + 1
    
    freq_floor  = iso_freq_list[index_floor]
    freq_ceil   = iso_freq_list[index_ceil]
    
    fine_freq_list = np.linspace(freq_floor,freq_ceil,21) # last element is never needed
    
    closest_matching_index = np.argmin(abs(fine_freq_list-freq))
    fine_freq = fine_freq_list[closest_matching_index]
    
    freq_midi_val      = index_floor
    freq_fine_midi_val = closest_matching_index
    if (closest_matching_index >10):
      freq_midi_val = index_ceil
      freq_fine_midi_val = closest_matching_index - 20
    
    freq_fine_midi_val += 9
    
    return (freq_midi_val,freq_fine_midi_val)
    
  
  
  bandwidth_mem = {}
  freq_mem      = {}
  
  def __init__(self):
    try:
      self.output = mido.open_output('CH345 MIDI 1') # this is the logilink midi thing
    except:
      pass
    
  def set_gain(self,filter_chan,gain):
    self.select_filter_chan(filter_chan)
    # set gain for current filter : value = 0-64
    # value 48 is +0dB, value 48+x is +x dB, 48-x is -x dB, it is that easy
    try:
      self.output.send(mido.Message('control_change', control=16, value=gain+48))
    except:
      pass
    
  def set_bandwidth(self,filter_chan,bandwidth):
    
    #if filter_chan in self.bandwidth_mem:
      #if self.bandwidth_mem[filter_chan] == bandwidth:
        #return
    
    self.select_filter_chan(filter_chan)
    # value is in 1/60 octaves, argument bandwith is given in octaves
    try:
      self.output.send(mido.Message('control_change', control=15, value=int(bandwidth*60.)))
    except:
      pass
    self.bandwidth_mem[filter_chan] = bandwidth
    
  def set_freq(self,filter_chan,freq):
      
    #if filter_chan in self.freq_mem:
      #if self.freq_mem[filter_chan] == freq:
        #return
    freq_midi_val, freq_fine_midi_val = self.find_fine_freq(freq)
    
    self.select_filter_chan(filter_chan)
    try:
      # coarse value
      self.output.send(mido.Message('control_change', control=13, value=int(freq_midi_val)))
      # fine value
      self.output.send(mido.Message('control_change', control=14, value=int(freq_fine_midi_val)))
    except:
      pass
    self.freq_mem[filter_chan] = freq
    

  def select_filter_chan(self,filter_chan):
    # select filter : value = 0-11
    if(filter_chan != self.filter_chan): ## only send if different channel is selected
      try:
        self.output.send(mido.Message('control_change', control=10, value=filter_chan))
      except:
        pass
      self.filter_chan = filter_chan
    

my_eq = behringer_eq()

app = Flask(__name__)

@app.route('/')
def index():
    #return 'Hello world'
    return render_template('eq.html') # has to be located in ./templates/

@app.route('/set_eq')
def set_eq():
    #a = int(request.args.get('a', 0))
    freq = int(request.args.get('freq', 500))
    bandwidth = float(request.args.get('bandwidth', 0.66))
    filter_chan = int(request.args.get('filter_chan', 0))
    gain = int(request.args.get('gain', 0))
    
    time.sleep(0.02)
    my_eq.set_freq(filter_chan,freq)
    my_eq.set_bandwidth(filter_chan,bandwidth)
    my_eq.set_gain(filter_chan,gain)
    
    return jsonify({
        "dummy" : 0
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
