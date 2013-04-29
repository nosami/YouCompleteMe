#!/usr/bin/env python
#
# Copyright (C) 2011, 2012  Stephen Sugden <me@stephensugden.com>
#                           Strahinja Val Markovic <val@markovic.io>
#
# This file is part of YouCompleteMe.
#
# YouCompleteMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YouCompleteMe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YouCompleteMe.  If not, see <http://www.gnu.org/licenses/>.

import vim
from threading import Thread, Event
from completers.completer import Completer
import vimsupport

#import sys

# Import stuff for Omnisharp
import urllib2, urllib, urlparse, logging, json, os, os.path #, cgi
#from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#from SocketServer import ThreadingMixIn

#Config for Omnisharp
logger = logging.getLogger('omnisharp')
logger.setLevel(logging.WARNING)

log_dir = os.path.join(vim.eval('expand("<sfile>:p:h")'), '..', 'log')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
hdlr = logging.FileHandler(os.path.join(log_dir, 'python.log'))
logger.addHandler(hdlr) 

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)


class CsharpCompleter( Completer ):
  """
  A Completer that uses the Jedi completion engine.
  https://jedi.readthedocs.org/en/latest/
  """

  def __init__( self ):
    super( CsharpCompleter, self ).__init__()
    self._query_ready = Event()
    self._candidates_ready = Event()
    self._candidates = None
    self._start_completion_thread()


  def _start_completion_thread( self ):
    self._completion_thread = Thread( target=self.SetCandidates )
    self._completion_thread.daemon = True
    self._completion_thread.start()


  def SupportedFiletypes( self ):
    """ Just csharp """
    return [ 'cs' ]


  def CandidatesForQueryAsyncInner( self, unused_query, unused_start_column ):
    self._candidates = None
    self._candidates_ready.clear()
    self._query_ready.set()


  def AsyncCandidateRequestReadyInner( self ):
    return WaitAndClear( self._candidates_ready, timeout=0.005 )


  def CandidatesFromStoredRequestInner( self ):
    return self._candidates or []


  def SetCandidates( self ):
    while True:
      try:
        WaitAndClear( self._query_ready )

        self._candidates = [ { 'word': str( completion['CompletionText'] ),
                               'menu': str( completion['Description'] ),
                               'info': str( completion['DisplayText']) }
                            for completion in self.getCompletions() ]
      except:
        self._query_ready.clear()
        self._candidates = []
      self._candidates_ready.set()


  def getCompletions(self):
    '''Ask server for completions'''
    js = self.getResponse('/autocomplete')
    if(js != ''):
      completions = json.loads(js)
      return completions
    return []
  
  
  def getResponse(self, endPoint, additionalParameters=None):
    '''Handle communication with server'''
    parameters = {}
    parameters['line'], parameters['column'] = vimsupport.CurrentLineAndColumn()
    parameters['buffer'] = '\n'.join( vim.current.buffer )
    parameters['filename'] = vim.current.buffer.name

    if(additionalParameters != None):
      parameters.update(additionalParameters)

    target = urlparse.urljoin(vim.eval('g:OmniSharp_host'), endPoint) #default is 2000, set in my vimrc
    parameters = urllib.urlencode(parameters)
    try:
      response = urllib2.urlopen(target, parameters)
      return response.read()
    except:
      vim.command("echoerr 'Could not connect to " + target + "'")
      return ''

def WaitAndClear( event, timeout=None ):
  # We can't just do flag_is_set = event.wait( timeout ) because that breaks on
  # Python 2.6
  event.wait( timeout )
  flag_is_set = event.is_set()
  if flag_is_set:
    event.clear()
  return flag_is_set
