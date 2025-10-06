##############################################
#        PTV Vision Code sample              #
#					                         #
# Define graphic parameters for line bars    #
# classified by TSys                         #
# (c) PTV Group, 2014  		                 #
# Use at your own risk, no warranty provided #
##############################################

import win32com.client
import sys,os

Visum = win32com.client.Dispatch("Visum.Visum")
Visum.LoadVersion(os.path.join(os.path.dirname(sys.argv[0]),"..","Example.ver"))

#// #region EmbeddedExample

myBar = Visum.Net.GraphicParameters.LinkGroup.GetBar(1)
myBar.SetAttValue("BarType", 2) # line bar
myBar.FillStyleLine.SetAttValue("AggrType", 0) # LinePathType_TSys

tsysBus = Visum.Net.TSystems.ItemByKey("B")
busGPA = myBar.FillStyleLine.Classify(tsysBus)
busGPA.SetAttValue("DrawPolygon", True)
busGPA.FillStyle.SetAttValue("FillColor", "FF30FF60")
myBar.FillStyleLine.SetPosition(tsysBus, 1)

#endregion