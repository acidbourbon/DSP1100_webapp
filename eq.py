#!/usr/bin/env python3

from flask import Flask, jsonify, render_template, request
import time

import mido

class behringer_eq:
  output = None
  filter_chan = -1
  
  def __init__(self):
    self.output = mido.open_output('CH345 MIDI 1') # this is the logilink midi thing
    
  def set_gain(self,filter_chan,gain):
    self.select_filter_chan(filter_chan)
    # set gain for current filter : value = 0-64
    # value 48 is +0dB, value 48+x is +x dB, 48-x is -x dB, it is that easy
    self.output.send(mido.Message('control_change', control=16, value=gain+48))
    

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
    print("received a={:d}".format(a))
    #b = int(request.args.get('b', 0))
    #div = 'na'
    #if b != 0:
        #div = a/b
    my_eq.set_gain(0,a)
    time.sleep(0.02)
    
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
