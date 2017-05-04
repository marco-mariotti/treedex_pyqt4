from .methods import *
from .data import *

def split_parameters(s, sep=';'):
  """ From a string like:    opt1=value;opt2=value2;opt3=val3 etc
      To a dict   {'opt1':'value', 'opt2':'value2', 'opt3':'val3'}"""
  out={}
  splt=s.split(sep)
  for minis in splt:
    k, v=minis.split('=')
    out[k]=v
  return out

class DCO_pgls(DCO):
  """ perform a pgls on the first two columns on the input DF. The column Node must be present. Syntax:      
  mode=best
with possibilities for mode:   self.possible_values['mode']
  """
  name='pgls'
  possible_values={'mode':['best', "Null", "BM","lambda", "OU"]}
  descriptions=   {'mode':{'best':'Best (by ML)', "Null":"Null (no tree)", "BM":"Brownian Motion", "lambda":"Pagel's lambda", "OU":"Ornstein-Uhlenbeck"}}
  default_dcow_parameters='mode=BM'
  default_parameters=None  #use this to define the default parameters of smart subclasses
  # def __init__    
  # def expand_parameters(self, parameters):    
  #     raise Exception, "ERROR expand_parameters must be defined in DCO_smart subclasses"
  # def backtrace_parameters(self, parameters): 
  #     raise Exception, "ERROR expand_parameters must be defined in DCO_smart subclasses"

  def action(self, df):
    x=self.interpreted_params(df)
    param_dict=split_parameters(x)
    mode=param_dict['mode']
    df=df.set_index('Node', inplace=False)
    #print df
    y_field= df.columns[0] #x_field_index];      #x_field_index=0;     y_field_index=1; 
    #y_field= df.columns[1] #y_field_index]
    fulltree=self.container.master().trees().get_tree(None) #default tree

    ydict={}; 
    for species in df.index:
      y=df.at[species, y_field]
      if pd.notnull(y): ydict[species]=y

    out=pd.DataFrame(columns=['y', 'x', 'mode', 'pvalue', 'intercept', 'slope', 'logL'])
    for x_field in df.columns[1:]:
      try:
        if not pd.types.common.is_numeric_dtype(  df.dtypes[x_field]  ): 
          print 'SKIPPING xfield not numeric: '+x_field
          continue
        xdict={}
        for species in df.index:
          x=df.at[species, x_field]
          if pd.notnull(x): xdict[species]=x

        nodes_this_test=set( [n.name  for n in fulltree if n.name in xdict and n.name in ydict] )
        if not nodes_this_test: 
          print 'SKIPPING no overlap in available nodes for x: {}  y: {}'.format(x_field, y_field)
          continue
        tree=fulltree.copy_topology()
        tree.prune(nodes_this_test)

        rx=rdataframe( {  species: xdict[species]     for species in df.index   if species in nodes_this_test} )
        ry=rdataframe( {  species: ydict[species]     for species in df.index   if species in nodes_this_test} )
        rtree=r_readtree(text=tree.write(format=1))

        if mode !='best':
          try:
            rout=simings.FUN_CUSTOM_pgls(rx, ry, rtree, mode)  #rpy2.robjects.vectors.ListVector
            # vcv.matrix   x.matrix y.matrix   residual  RSS  n   npar   df   sigma2.ols  sigma2.ml  estimate logLik
            logL= rout.rx('logLik')[0].rx('logL')[0]
            intercept, slope      =        rout.rx('estimate')[0].rx('coef')[0]      
            intercept_pvalue, slope_pvalue = rout.rx('estimate')[0].rx('p.val')[0]      
            res=pd.Series({'logL':logL,  'slope':slope, 'intercept':intercept, 'pvalue':slope_pvalue, 'mode':mode, 'x':x_field, 'y':y_field} )
            out=out.append(res, ignore_index=True)
          except RRuntimeError:
            printerr( '{k}: ERROR on runtime!'.format(k=self.key()), 1)
            #raise
        else: 
          try:
            rout=simings.FUN_CUSTOM_pgls_full(rx, ry, rtree) ##rpy2.robjects.vectors.ListVector
            modes_ordered_by_likel = sorted( list(self.possible_values['mode']), key=lambda x:rout.rx(x)[0].rx('logLik')[0].rx('logL')[0] if not rout.rx(x)[0] == RNull else None  )
            best_mode= modes_ordered_by_likel[-1]
            logL= rout.rx(best_mode)[0].rx('logLik')[0].rx('logL')[0]
            intercept, slope=        rout.rx(best_mode)[0].rx('estimate')[0].rx('coef')[0]      
            intercept_pvalue, slope_pvalue = rout.rx(best_mode)[0].rx('estimate')[0].rx('p.val')[0]      
            res= pd.Series({'logL':logL,  'slope':slope, 'intercept':intercept, 'pvalue':slope_pvalue, 'mode':best_mode, 'x':x_field, 'y':y_field } )
            out=out.append(res, ignore_index=True)
          except RRuntimeError:
            printerr( '{k}: ERROR on runtime!'.format(k=self.key()), 1)
            #raise
      except: 
        printerr( 'ERROR with x: {} y: {}'.format(x_field, y_field), 1)
        raise
    print out
    return out 

DCO_name2class['pgls']=DCO_pgls

class DCO_colorGradient(DataChannelOperation):
  """ Parameter: colorspace like    r0.0:rrggbb,0.5:rrggbb,1.0:rrggbb            
       optionally with suffix   ;rrggbb    for the color of NaN/None values; otherwise this is taken from 
       optionally preceded by colname@ if you wanted. Otherwise it's the first column.
      The first letter of colorspace can be r (for RGB) or h (for HSV) which is the space in which intermediate colors are computed by interpolation
 For the values in that column the input DF, computes its position in the colorspace (which is a RRGGBB color).
 Output has same number of rows as input, and an additional column: color
 The values here is the new color in RRGGBB.  Note that the max and minimum in the input DF per column is considered to fix the limits
 """
  name='colorGradient'
  def action(self, df):
    ip=self.interpreted_params(df)
    splt=ip.split('@')
    if len(splt)==2:     column=splt[0];        s=splt[1]
    else:                column=df.columns[0];  s=splt[0]
    splt=s.split(';')
    s=splt[0]    
    if len(splt)==2:     default_color=splt[1]
    else:                default_color=self.master().colors().get_default_color()
    color_mode=s[0]  # r or h
    idf=df.loc[:,column]  # this is a series
    if not pd.types.api.is_numeric_dtype(idf): raise Exception, "ERROR DCO_gradient requires a numeric input! The column {} has instead type: {}".format(column, idf.dtype)
    vmin=idf.min()
    vmax=idf.max()
    # now s is like r0.0:rrggbb,0.5:rrggbb,1.0:rrggbb
    ticks=[]   # [  [0.0, [ dec_r, dec_g, dec_b ]],   [1.0, [dec_r, dec_g, dec_b]]  ]
    for block in s[1:].split(','):
      p,color=block.split(':')
      pos=float(p)
      r=int(color[:2], 16)
      g=int(color[2:4], 16)
      b=int(color[4:], 16)
      ticks.append([pos, [r,g,b]])

    next_df=df.assign(color=default_color)
    for i, row_i in enumerate(idf.index):
      value=idf.iat[i]
      if pd.isnull(value): continue

      x=rescale(float(value), 0.0, 1.0, vmin, vmax)  # between 0.0 and 1.0   
      ### following code is adapted from pg.widgets.GradientEditorItem.getColor to have a good correspondance with the color in the gradient widget
      if x <= ticks[0][0]:        r,g,b = ticks[0][1]
      elif x >= ticks[-1][0]:     r,g,b = ticks[-1][1]
      else:
        x2 = ticks[0][0]
        for i in range(1,len(ticks)):
          x1 = x2
          x2 = ticks[i][0]
          if x1 <= x and x2 >= x:            break
        dx = (x2-x1)
        if dx == 0:          f = 0.
        else:                f = (x-x1) / dx
        c1 = ticks[i-1][1] #.color
        c2 = ticks[i][1]   #.color
        if   color_mode=='r': #      self.gradient['mode'] == 'rgb':
          r = int( c1[0] * (1.-f) + c2[0] * f )
          g = int( c1[1] * (1.-f) + c2[1] * f )
          b = int( c1[2] * (1.-f) + c2[2] * f )
          #a = 255 #c1[3] * (1.-f) + c2[3] * f
        elif color_mode=='h': #     self.gradient['mode'] == 'hsv':
          r1,g1,b1=c1[:3] #0-255 
          r2,g2,b2=c2[:3] #0-255
          h1,s1,v1=rgb_to_hsv(r1/255.0, g1/255.0, b1/255.0)  #0-1
          h2,s2,v2=rgb_to_hsv(r2/255.0, g2/255.0, b2/255.0)  #0-1
          h = h1 * (1.-f) + h2 * f
          s = s1 * (1.-f) + s2 * f
          v = v1 * (1.-f) + v2 * f
          r,g,b= map(lambda x: int(x*255),  hsv_to_rgb(h,s,v))     #0-255
        else: raise Exception, "ERROR DCO_gradient unrecognized color mode! Expected r (RBG) or h (HSV) but received: {}".format(mode)

      color='{r:02X}{g:02X}{b:02X}'.format(r=r, g=g, b=b)
      next_df.at[row_i, 'color']=color
    return next_df


DCO_name2class['colorGradient']=DCO_colorGradient


# class DCO_colormap_define(DCO_define):
#   """ """
#   def channel_dataframe(self, df, mu): return DCO_call.channel_dataframe(self, df, mu, target_fn=self.container.master().colors().colormap_was_defined)

class DCO_colormap_call(DCO_call):
  """ """
  name='colormap_call'
  def extend_run_chain(self, run_chain, index):  
    return  DCO_call.extend_run_chain(self, run_chain, index, target_container=self.container.master().colors())
                                                                  
DCO_name2class['colormap_call']=DCO_colormap_call


class DCO_color(DCO_smart):  
  name='color'
  """ Mode #1:  f|RRGGBB       for fixed color for every row   (RR, GG, BB are hex codes for color)
      Mode #2:  g|colorspace   for gradient ; colorspace is exaclty as the input parameters of DCO_gradient (including column and default_color
      Mode #3:  m|mapname      for invoking existing colormap
.. to do: categorical as c|    """ 
  default_parameters='f|777777'
  def expand_parameters(self, parameters):    
    if   parameters.startswith('f|'):         return 'f[add_column:color=@{c}]'.format(c=parameters[2:])   
    elif parameters.startswith('g|'):         return 'g[colorGradient:{cs}]'.format(cs=parameters[2:])        
    elif parameters.startswith('m|'):         return 'm[colormap_call:{cm}]'.format(cm=parameters[2:])        
    else: 
      raise Exception, "ERROR DCO_color wrong syntax: {}".format(parameters)

  def backtrace_parameters(self, parameters): 
    if   parameters.startswith('f'):    return 'f|'+parameters[20:-1]  #     parameters.split('@')[1][:-1] 
    elif parameters.startswith('g'):    return 'g|'+parameters[16:-1] 
    elif parameters.startswith('m'):    return 'm|'+parameters[16:-1] 
    else: 
      raise Exception, "ERROR DCO_color wrong syntax: {}".format(parameters)

  def short(self): 
    if not self.parameters: return 'None'
    elif self.parameters.startswith('f'):    return self.backtrace_parameters(self.parameters)[2:]
    elif self.parameters.startswith('g'):    return '<gradient>'
    elif self.parameters.startswith('m'):    return self.backtrace_parameters(self.parameters)[2:]
    else: 
      return self.backtrace_parameters(self.parameters)

DCO_name2class['color']=DCO_color
#self.container.master().trees().default_tree.tree_name
