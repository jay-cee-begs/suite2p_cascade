import os
import sys

from pathlib import Path
SUITE2P_PATH=f"{Path.home()}/Code/suite2p" #Where we expect to find the file folder for suite2p
import pandas
os.environ["path"] = os.environ["path"] + r"C:\Users\Justus\anaconda3\envs\suite2p\Library\bin" #Suite2p env in (Ana)conda
import matplotlib 
matplotlib.use('Qt5Agg')
#import tifffile
class Dummy:
  ROIList = None # for sima.ROI
  #tifffile = tifffile # for sima.misc
  class motion: # for sima
    MotionEstimationStrategy = object
  class speedups:
    available = False # For Shapely.speedups

def suite2PLoad():
  import sys
  print ("Home", Path.home())
  CELLPOSE_PATH=f"{Path.home()}\\Code\\cellpose"
  #if CELLPOSE_PATH not in sys.path:
  #  sys.path.insert(0, CELLPOSE_PATH)
  #import cellpose
  #sys.modules["cellpose"] = cellpose
  #if SUITE2P_PATH not in sys.path:
  #  sys.path.insert(0, SUITE2P_PATH)
  import suite2p as run_s2p
  sys.modules["suite2p"] = run_s2p
  print("Done")
  return run_s2p


run_s2p = suite2PLoad()
def runS2pGUI():
  import os
  org_dir = os.path.abspath(os.path.curdir)
  os.chdir(SUITE2P_PATH)
  run_s2p.run_gui()
  os.chdir(org_dir)

runS2pGUI()