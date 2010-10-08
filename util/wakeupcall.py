#!/usr/bin/env python
#
#
#modified from Mark Welch.
#dadamson added conference calling
#uses Skype4Py - it *may* necessary to patch it as per
# http://forum.skype.com/index.php?showtopic=357681 - but I'm not sure
#also on the mac, Skype is 32-bit, Python is 64-bit.
# you must run 32-bit python to be compatible with skype:
# $ defaults write com.apple.versioner.python Prefer-32-Bit -bool yes

# Documentation in reStructuredText format,
# http://docutils.sourceforge.net/rst.html
__docformat__ = 'restructuredtext'

"""
==================
Wakeup call script
==================

Overview
--------

This script will use Skype to place a call to a contact or a telephone
number, then play one or more audio files.

Usage
-----

Command line invocation:

    wakeupcall *target*[,*target*...] *sound*[,*sound*...]

Each *target* can be a phone number (with leading '+', country and area code)
or a contact name from the Skype contacts list, separated by commas.

Each *sound* is the name of a sound file to play, separated by
commas. Sound files currently MUST be in Microsoft WAV format, 16
signed bits per sample, 1 channel, 16KHz sample rate. To convert from
(for example) an mp3, use a recent version of sox as follows:

    sox infile.mp3 -r 16k -c 1 -b 16 outfile.wav

Operational notes
-----------------

The Skype API, as far as I can tell, does not allow one to 
associate call objects with Python objects. The sample scripts 
use globals to track calls. For the time being, when this script 
initiates a new call, the next unattached call that is reported 
as being in ROUTING status will be attached to any AutoCaller
instance waiting for a call assignment. (See source)

Attempting to operate the Skype GUI while this script initiates 
a call will lead to unpredictable behavior.

Calling a number that is outside your calling plan will cost you
Skype Credit. Be careful.

Requirements
------------

- Python_, versions up to 2.6
- Skype_, tested with 2.7 on Mac OS X 10.5
- `Skype4Py toolkit`_

Platforms
---------

Tested only on Mac OS X 10.5, but no known issues
impede operation on other platforms.

.. _Python: http://www.python.org
.. _Skype: http://www.skype.com
.. _Skype4Py toolkit: http://bit.ly/WWOIl

License
-------

This code is in the public domain. The author is not responsible for
any use or misuse of this script. Use it at your own risk.

:Date: 2009-June-13
:Authors:

    Mark Welch <mw@splode.com>

"""

import getopt
import os
import os.path
import sys
import time
import wave

from operator import and_
import Skype4Py
import threading

#
# Logging/tracing support
#

verbose_flag = False
quiet_flag = False

def info(msg):
    """
    Report information to standard output if the quiet flag
    (-q) has not been set.

    `msg` - The message to report (string).
    """
    if not quiet_flag:
        sys.stdout.write(msg + "\n")

def verbose(msg):
    """
    Report information to standard output if the verbose flag 
    (-v) has been set.

    `msg` - The message to report (string).
    """
    if verbose_flag:
        sys.stdout.write(msg + "\n")

def warn(msg):
    """
    Report a warning to stderr.
    
    `msg` - The message to report (string).
    """
    sys.stderr.write("Warning: %s\n" % msg)

def error(msg):
    """
    Report a fatal error to stdout, and exit the script.
    
    `msg` - The message to report (string).
    """
    sys.stderr.write("Error: %s\n\n" % msg)
    sys.exit(1)

def usage(msg, exitcode=1):
    """
    Report an error to stdout, describe script usage, and exit.
    
    `msg` - The message to report (string).
    `exitcode` - The exit code for this process, passed to sys.exit (int).
    """
    sys.stderr.write("\nError: %s\n\n" % msg)
    sys.stderr.write("Usage: %s [-q] [-v] "
                     "<target>[,<target>...] <soundfile>[,<soundfile>...]\n"
                     % sys.argv[0]) 
    sys.stderr.write("\nEach <target> can be a phone number (with leading '+',\n"
                     "country and area code), "
                     "or a contact name from the \nSkype contacts list.\n"
                     "Separate targets with commas.")
    sys.stderr.write("\n<soundfile> is the name of one or more "
                     "sound files to play, \n"
                     "separated by commas. Sound files currently MUST be\n"
                     "in Microsoft WAV format, 16 signed bits per sample,\n"
                     "1 channel, 16KHz sample rate.\n\n")
    sys.exit(exitcode)

#
# Skype support
#

#: Codes returned by Skype to indicate call termination.
CALL_TERMINATIONS = [Skype4Py.clsFailed, Skype4Py.clsFinished, 
                     Skype4Py.clsMissed, Skype4Py.clsRefused,
                     Skype4Py.clsBusy, Skype4Py.clsCancelled]

#: Caller objects whose calls have been placed locally,
#: but not in Skype.
pending_callers = []

#: Caller objects whose calls have been placed in Skype.
assigned_callers = {}

global queued_callers
queued_callers= []

def place_call(caller, target_list):
    """
    Place a call through Skype.
    
    `caller` - A SkypeCaller instance which will manage the call.
    `target_list` - A list of telephone numbers and/or contact names to call.

    Returns None.
    """
    pending_callers.append(caller)
    skype.PlaceCall(*target_list)

def next_pending_caller():
    """
    Locate and return the next available SkypeCaller object
    in the pending caller queue.
    
    Returns the SkypeCaller instance which will manage the next call.
    """
    try:
        rv = pending_callers.pop(0)
    except IndexError:
        rv = None
    return rv

def get_caller_for_call(call):
    """
    Locate and return the SkypeCaller object assigned to a given call.

    `call` - An `ICall` instance representing the call.

    Returns the SkypeCaller instance which will manage the next call.
    """
    id = call.Id
    if assigned_callers.has_key(id):
        rv = assigned_callers[id]
    else:
        rv = next_pending_caller()
        if(rv):
            rv.attach_to_call(call)
            assigned_callers[id] = rv
        else:
            rv = assigned_callers.values()[0]
            rv.attach_to_call(call)
            assigned_callers[id]=rv
    return rv

def on_attach(status):
    """
    Callback function, called by Skype4Py when this process attaches
    to, or detaches from, the Skype client.

    `status` - A boolean indicating whether we are attached to Skype.
    """
    verbose("API attachment status: %s" % 
            skype.Convert.AttachmentStatusToText(status))
    # XXX Broadcast this status to all callers?

def on_call(call, status):
    """
    Callback function, called by Skype4Py when a call changes
    state within the Skype client.

    `call` - The ICall instance representing the call.
    `status` - A string identifying the new call status.
    """
    if(get_caller_for_call(call)):
        get_caller_for_call(call).on_call_status(call, status)
    #else:
    #    print "no caller for %s, status %s", call, status

def on_input_status_change(call, status):
    """
    Callback function, called by Skype4Py when the input device
    for a call within the Skype client changes state.

    `call` - The ICall instance representing the call.
    `status` - A boolean identifying the new input status.
    """
    if(get_caller_for_call(call)):
        get_caller_for_call(call).on_input_status_change(call, status)
    #else:
    #    print "no caller for %s, status:%s", call, status

def setup_skype():
    """
    Initialize the Skype toolkit, launch the Skype client
    if it is not already running, and attach to it.
    """
    global skype
    
    try:
        skype
    except NameError:
        skype = Skype4Py.Skype()
        skype.OnAttachmentStatus = on_attach
        skype.OnCallStatus = on_call
        skype.OnCallInputStatusChanged = on_input_status_change
    
        # Start Skype if it's not already running.
        if not skype.Client.IsRunning:
            verbose("Starting Skype.")
            skype.Client.Start()

        # Attach to Skype.
        verbose("Attaching to Skype.")
        skype.Attach()

#
# SkypeCaller class
#

class SkypeCaller(object):
    """
    A class which sets up and operates Skype calls.
    """
    def __init__(self, target_list):
        """
        Constructor.
        `target_list` - The contacts and/or numbers to call.
        Numbers must have leading '+' and country/area codes.
        """
        self.calls = []
        self.call_states = {}
        self.target_list = target_list
        self.hung_up = False
        #self.has_connected = False

    def attach_to_call(self, call):
        """
        Associate this caller with a call in progress.
        `call` - an ICall instance from the Skype4Py toolkit.
        """
        self.calls.append(call)

    def on_call_status(self, call, status):
        """
        Notify this caller of a status update for this caller's call.
        `status` - A string identifying the new call status.
        """
        verbose("%s status: %s (%s)" % 
                (call, status, skype.Convert.CallStatusToText(status)))
        self.call_states[call] = status
        if status == Skype4Py.clsInProgress:
            #self.has_connected = True
            self.call_status_connected(call)
        if status == Skype4Py.clsEarlyMedia:
            self.call_status_early_media(call)
        if status in CALL_TERMINATIONS:
            self.call_status_terminated(call)

    def on_input_status_change(self, call, status):
        """
        Notify this caller instance of a change in the input status
        for its associated call.
        `status` - A boolean indicating the input status.
        """
        if(not call in self.calls):
            self.calls.append(call)
        verbose("Input status change for call %s: device %s, status %s"
                % (call, call.InputDevice(), status))

    def call_status_is_terminated(self):
        """
        Return True if this call has been terminated,
        False otherwise.
        """

        return self.call_states and reduce(and_, [call_status in CALL_TERMINATIONS for call_status in self.call_states.values()])

    def call_status_connected(self, call):
        """
        This method is called when this instance's call
        has connected. Overridden in subclasses.
        """
        pass

    def call_status_early_media(self, call):
        """
        This method is called when the call associated with this 
        object is ready to receive device and other configuration 
        changes while a call is pending.

        Overridden in subclasses.
        """
        pass

    def call_status_terminated(self, call):
        """
        This method is called when the call associated with this 
        object has been terminated.

        Overridden in subclasses.
        """
        verbose("Call terminated")

    def place_call(self):
        """
        This method places a call within the Skype client.
        """
        place_call(self, self.target_list)

    def hangup(self):
        """
        Hang up this call.
        """
        if not self.hung_up:
            for call in self.calls:
                if (call.Status == Skype4Py.clsInProgress):
                    #print "finishing %s " % call
                    call.Finish()
                    #print "finished %s " % call
        self.hung_up = True

    def wait_for_hangup(self):
        """
        Wait until the call associated with this caller
        has terminated.
        """
        while not self.call_status_is_terminated():
            time.sleep(0.1)

#
# WakeupCall class
#

class WakeupCall(SkypeCaller):
    """
    A subclass of SkypeCaller which plays one or more
    sound files at the recipient. Once a call is connected,
    the first sound file in the queue is played. After that,
    subsequent input status changes (indicating the end of
    play of the previous sound file) triggers the loading of
    subsequent sound files from the queue.
    """
    def __init__(self, target_list, sounds):
        """
        Constructor.
        `target_list` - The numbers or contacts to call.
        `sounds` - A list of pathnames of sound files to play.
        """
        super(WakeupCall, self).__init__(target_list)
        self.sound_list = sounds
        self.wait_sound = None
        
        self.pending_sound = None
        self.setting_sound = False

    def call_status_terminated(self, call):
        """
        Called by SkypeCaller when the call associated
        with this caller has been terminated.
        """
        super(WakeupCall, self).call_status_terminated(call)

    def call_status_connected(self, call):
        """
        The underlying call has been connected.
        Begin playing sounds at the recipient.
        """
        
        #if not all callers are online 
        #(and we're able to as calls[0], given Skype or Skype4Py's broken nature)
        #play a "wait" sound
        if call == self.calls[0] and [c.Status for c in self.calls if c.Status != Skype4Py.clsInProgress]:
            if(self.wait_sound):
                print "adding wait sound..."
                self.sound_list.insert(0, self.wait_sound)
                
        self.process_sound_to_skype(call)

    def on_input_status_change(self, call, status):
        """
        The input device and/or status has changed.
        If we have been playing a sound file, queue the next one.
        """
        super(WakeupCall, self).on_input_status_change(call, status)
        if not self.setting_sound:
            if not status:
                # Last sound ran out, queue a new one.
                self.process_sound_to_skype(call)

    def process_sound_to_skype(self, call):
        """
        Begin playing the next sound in the list of sounds
        to the recipient of this call.
        """
        #only calls[0] (the first call in the conference) 
        #appears to respond to ALTER commands, including changing input
        #and hanging up, resulting in SkypeError: [Errno 11] Invalid call id
        try:
            try:
                if(call == self.calls[0]):
                    self.setting_sound = True
                    next_sound = self.sound_list.pop(0)
                    #print "popped %s"% next_sound
                    #print "%d remaining"% len(self.sound_list)
                    self.pending_sound = next_sound
                    verbose("Playing sound '%s' at recipient." % next_sound)
                    # XXX construct full path if not provided
                    # if next_sound[0] != '/': etc
                    call.InputDevice(Skype4Py.callIoDeviceTypeFile, next_sound)
    
                    # Not clear why, but it seems necessary to wait 1 second
                    # after setting the input device.
                    # XXX diagnose and fix
                    time.sleep(1.0)
    
                    verbose("After 1 second, input device is %s" 
                            % call.InputDevice())
            except IndexError:
                # All done with sounds
                print "I should hang up now: %s: %s" % (call.Id, call.Status)
                time.sleep(1.0)
                #call.Finish()
                #Finish() seems to be broken for Conference calls:
                #the first call will finish, subsequent attempted calls report
                #SkypeError: [Errno 11] Invalid call id
            except Exception as e:
                print e
                print e.args
        finally:
            self.setting_sound = False

def dummy():
    print("*starting dummy thread %s" % threading.current_thread())
    time.sleep(10.0)
    print("*done with dummy thread %s" % threading.current_thread())

def call_all_thread(target_list, wav_list, wait_sound=None):
    #threading.Thread(target=dummy).start()
    threading.Thread(target=call_all, args=(target_list, wav_list, wait_sound)).start()

def call_all(target_list, wav_list, wait_sound=None):
    """
    target_list is a list of phone numbers in +14125551234 form
    wav_list is a list of paths to WAV audio files to be played in sequence.
    all targets will be conferenced, and will hear the audio simultaneously.
    """
    #setup_skype is conditioned not to run more than once.
    setup_skype()
    
    print "call %s" % target_list
    
    for target in target_list:
        # Raw phone numbers are ok.
        found = (target[0] == '+')
        
        # Look for contact in contact list.
        if not found:
            for f in skype.Friends:
                if f.Handle == target:
                    found = True
        if not found:
            print "Target '%s' not found in contact list and will not be called" % target
            target_list.remove(target)

    wav_list = [os.path.abspath(p) for p in wav_list]

    # Check format and path of sound files.
    for wav_file in wav_list:
        reader = wave.open(wav_file)
        params = reader.getparams()
        reader.close()
        ok = params[:3] == (1, 2, 16000) and params[3] > 0
        if not ok:
            print "File %s not in proper format\n(need mono/16-bit/16000 Hz)\nIt will not be played." % wav_file
            wav_list.remove(wav_file)        
    
    # Instantiate an AutoCaller.
    wc = WakeupCall(target_list, wav_list)
    if(wait_sound):
        wc.wait_sound = os.path.abspath(wait_sound)
        
    #this is a stupid way to queue. should spawn a thread?
    global queued_callers

    if(skype.ActiveCalls.Count == 0):
        # Place the call, wait for call to end.
        wc.place_call()
        wc.wait_for_hangup()
        
        while(queued_callers):
            wc = queued_callers.pop(0)
            wc.place_call()
            wc.wait_for_hangup()
    else:
        queued_callers.append(wc)
        print ["queued: %s"% q.target_list for q in queued_callers]

def main():
    """
    Main function, called when this script is run from the shell.
    """
    # Parse command line arguments.
    try:
        option_list, args = getopt.getopt(sys.argv[1:], 'qv')
    except GetoptError, ge:
        # Bad option, no biscuit.
        usage(ge.msg)

    global quiet_flag, verbose_flag
    for k, v in option_list:
        if k == '-q':
            quiet_flag = True
            verbose_flag = False
        elif k == '-v':
            quiet_flag = False
            verbose_flag = True


    target_list = [p for p in args[0].split(',') if p]
    wav_list = [os.path.abspath(p) for p in args[1].split(',') if p]
    
    if not wav_list:
        usage("Must specify a sound file")

    if not target_list:
        usage("Must specify one or more targets, and one or more sound files")


    # Start the Skype client and attach to it,
    # so that we can search the contact list.
    #setup_skype()

    call_all(target_list, wav_list)

    # Options and files all check out at this point.
    # Instantiate an AutoCaller.
    #wc = WakeupCall(target_list, wav_list)

    # Place the call, wait for call to end.
    #wc.place_call()
    
    #wc.wait_for_hangup()



if __name__ == '__main__':
    main()
