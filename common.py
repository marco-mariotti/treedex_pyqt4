# bunch of functions from MMlib
opt={'no_colors':0, 'Q':0}
colored_keywords={}
printed_rchar=0
from string import join, lowercase, uppercase, lower, upper
import sys

def printerr(msg, put_newline=0, how='', keywords={}, is_service=False):
  global printed_rchar
  if not keywords and colored_keywords: keywords=colored_keywords
  msg=str(msg)
  if put_newline:    msg=msg+'\n'
  no_color_msg=msg
  if printed_rchar:
    sys.stderr.write('\r'+printed_rchar*' '+'\r' )
    printed_rchar=0
  if sys.stdout.isatty() and not opt['no_colors']:
    if how:
      for c in how.split(','): 
        if not terminal_codes.has_key(c): raise Exception, "ERROR option 'how' for write was not recognized: "+str(c)+' ; possible values are: '+join([i for i in terminal_codes.keys() if i], ',')
        msg=terminal_codes[c]+msg+terminal_codes['']
    for word in keywords:
      code=''
      for c in keywords[word].split(','): code+=terminal_codes[c]
      msg= replace(msg, word, code+word+terminal_codes[''])
  sys.stderr.write(str(msg))
  if not is_service and 'log_file' in globals(): print >> log_file, str(no_color_msg),
  
def service(msg):
  """ see write function"""
  msg=str(msg)
  global printed_rchar, opt
  if sys.stderr.isatty() and  not opt['Q']:
    if printed_rchar:
      printerr('\r'+printed_rchar*' ', is_service=True )
    printerr( "\r"+msg, is_service=True)
    printed_rchar=len(msg)
  #if 'log_file' in globals(): print >> log_file, str(msg+'\n') #putting a newline

def verbose(msg, put_newline=0):
  global opt
  if put_newline:    msg=str(msg)+'\n'  
  if opt['v']:
    write( msg )
    if 'log_file' in globals(): print >> log_file, str(msg),
    
terminal_codes={'':'\033[0m', 'red':'\033[31m', 'green':'\033[32m', 'black':'\033[30m', 'yellow':'\033[33m', 'blue':'\033[34m', 'magenta':'\033[35m', 'cyan':'\033[36m', 'white':'\033[37m', 'bright':'\033[1m', 'dim':'\033[2m', 'underscore':'\033[4m', 'blink':'\033[5m', 'reverse':'\033[7m', 'hidden':'\033[8m'}
def write(msg, put_newline=0, how='', keywords={}):
  """ Function to extend the functionalities of the standard 'print'. First argument (put_newline) when set to 1 put a newline after the string passed, as print would normally do. The argument "how" can be given a color to write the message in that color (only for atty terminals). This is prevented if opt['no_colors'] is active.  The function write is coupled with function "service" which prints service message which are deleted when another service message is printed, or another message is printed with the write function. If you use service, you should only print things with "write".
Argument keywords allows to use certain colors (or other "how" arguments) for certain keywords. The argument is a hash of keywords and correspoding how arguments. for example if you want to higlight all "ERROR" in red, pass keywords={'ERROR':'red'} 
"""
  msg=str(msg)
  global printed_rchar, opt
  if not keywords and colored_keywords: keywords=colored_keywords
  if put_newline:     msg=msg+'\n'
  no_color_msg=msg
  if sys.stdout.isatty() and not opt['no_colors']:
    if how:
      for c in how.split(','): 
        if not terminal_codes.has_key(c): raise Exception, "ERROR option 'how' for write was not recognized: "+str(c)+' ; possible values are: '+join([i for i in terminal_codes.keys() if i], ',')
        msg=terminal_codes[c]+msg+terminal_codes['']
    for word in keywords:
      code=''
      for c in keywords[word].split(','): code+=terminal_codes[c]
      msg= replace(msg, word, code+word+terminal_codes[''])
  if printed_rchar:
    sys.stderr.write('\r'+printed_rchar*' '+'\r' )
    printed_rchar=0
  sys.stdout.write(msg)
  if 'log_file' in globals(): print >> log_file, no_color_msg, 
warning=write
