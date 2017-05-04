from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage, importr
from rpy2.robjects import DataFrame as rdataframe
from rpy2.rinterface import RRuntimeError, NULL as RNull
import scipy.stats
import scipy.linalg
import os

siming_rcode=''.join(open(os.path.dirname(os.path.abspath(__file__))+'/PGLS.r').readlines())
simings=SignatureTranslatedAnonymousPackage(siming_rcode, 'simings')
r_readtree=importr('ape').read_tree
