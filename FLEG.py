#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab tabstop=4 shiftwidth=4


import wx
import wx.lib.wxcairo as wxcairo
import sys
import poppler
import subprocess
import inspect
import os

"""
    Using wxPDFViewer from Marcelo Fidel Fernandez
    http://www.marcelofernandez.info - marcelo.fidel.fernandez@gmail.com
"""

globalpath = os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe())))
if globalpath == '':
    globalpath = '.'


class PDFWindow(wx.ScrolledWindow):
    """ This example class implements a PDF Viewer Window, handling Zoom and Scrolling """

    MAX_SCALE = 20000
    MIN_SCALE = 0.0
    SCROLLBAR_UNITS = 20  # pixels per scrollbar unit

    def __init__(self, parent, filetype):
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY)
        # Wrap a panel inside
        self.panel = wx.Panel(self)
        # Initialize variables
        self.n_page = 0
        self.scale = 1
        self.initscale = 1.0
        self.document = None
        self.n_pages = None
        self.current_page = None
        self.width = None
        self.height = None
        self.filetype = filetype
        # Connect panel events
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.panel.Bind(wx.EVT_KEY_DOWN, self.DragFormula)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.DragFormula)
        #self.panel.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

    def LoadDocument(self, file):
        self.document = poppler.document_new_from_file("file://" + file, None)
        self.n_pages = self.document.get_n_pages()
        self.current_page = self.document.get_page(self.n_page)
        self.width, self.height = (325,160)#self.current_page.get_size()
        self.scale = min(325.0/self.current_page.get_size()[0],160.0/self.current_page.get_size()[1])
        self.initscale = self.scale
        self.panel.SetSize((self.width, self.height))

    def OnPaint(self, event):
        dc = wx.PaintDC(self.panel)
        cr = wxcairo.ContextFromDC(dc)
        cr.set_source_rgb(241.0/255, 240.0/255, 239.0/255)  # White background
        if self.scale != 1:
            cr.scale(self.scale, self.scale)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()
        self.current_page.render(cr)

    def OnLeftDown(self, event):
        self._UpdateScale(self.scale + 0.1)

    def OnRightDown(self, event):
        self._UpdateScale(self.scale - 0.1)

    def _UpdateScale(self, new_scale):
        if new_scale >= PDFWindow.MIN_SCALE and new_scale <= PDFWindow.MAX_SCALE:
            self.scale = new_scale
            # Obtain the current scroll position
            prev_position = self.GetViewStart()
            # Scroll to the beginning because I'm going to redraw all the panel
            self.Scroll(0, 0)
            # Redraw (calls OnPaint and such)
            self.Refresh()
            # Update panel Size and scrollbar config
            self._UpdateSize()
            # Get to the previous scroll position
            self.Scroll(prev_position[0], prev_position[1])

    def _UpdateSize(self):
        u = PDFWindow.SCROLLBAR_UNITS
        self.panel.SetSize((self.width*self.scale, self.height*self.scale))
        #self.SetScrollbars(u, u, (self.width*self.scale)/u, (self.height*self.scale)/u)

    def OnKeyDown(self, event):
        update = True
        # More keycodes in http://docs.wxwidgets.org/stable/wx_keycodes.html#keycodes
        keycode = event.GetKeyCode()
        if keycode in (wx.WXK_PAGEDOWN, wx.WXK_SPACE):
            next_page = self.n_page + 1
        elif keycode == wx.WXK_PAGEUP:
            next_page = self.n_page - 1
        else:
            update = False
        if update and (next_page >= 0) and (next_page < self.n_pages):
                self.n_page = next_page
                self.current_page = self.document.get_page(next_page)
                self.Refresh()

    def DragFormula(self, event):
        formuladata = wx.FileDataObject()

        if self.filetype == "pdf":
            formuladata.AddFile(globalpath+"/temp.pdf")

        if self.filetype == "png":
            formuladata.AddFile(globalpath+"/temp.png")

        if self.filetype == "svg":
            formuladata.AddFile(globalpath+"/temp.svg")


        datacomp = wx.DataObjectComposite()
        datacomp.Add(formuladata)

        dropsource = wx.DropSource(self)
        dropsource.SetData(datacomp)
        res = dropsource.DoDragDrop(flags=wx.Drag_CopyOnly)


class FLEG(wx.Frame):

    def __init__(self, parent, title):
        super(FLEG, self).__init__(parent, title=title,
            size=(360, 420))

        self.GUI()
        self.Centre()
        self.Show()
        self.LoadHistory()

    def GUI(self):

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        self.pdfwindow = PDFWindow(panel,'svg')
        self.pdfwindow.LoadDocument(globalpath+"/logo.pdf")
        self.pdfwindow.SetFocus()
        hbox1.Add(self.pdfwindow, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=8)


        hboxslider = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(hboxslider, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=0)
        self.slider = wx.Slider(panel, -1, 50, 0, 100, (10, 10), (320, 30),
        wx.SL_HORIZONTAL | wx.SL_AUTOTICKS )
        hboxslider.Add(self.slider, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=18)
        self.slider.Bind(wx.EVT_SLIDER, self.SliderUpdate)
        self.slider.Disable()

        vbox.Add((-1, 10))

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.tc2 = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        hbox2.Add(self.tc2, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)

        vbox.Add((-1, 10))

        hboxhist = wx.BoxSizer(wx.HORIZONTAL)
        self.combohist = wx.ComboBox(panel, -1, "History", (0, 0), (340,30), [], wx.CB_READONLY)
        hboxhist.Add(self.combohist)
        vbox.Add(hboxhist, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        self.combohist.Bind(wx.EVT_COMBOBOX, self.TakeFormulaFromHist)

        vbox.Add((-1, -60))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.combobox = wx.ComboBox(panel, -1, "svg", (100, 0), (80,30), ["pdf","png","svg"], wx.CB_READONLY)
        hbox3.Add(self.combobox)
        hbox3.Add((160, -1))

        btn1 = wx.Button(panel, label='Generate', size=(100, 30))
        hbox3.Add(btn1)
        vbox.Add(hbox3, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10)
        btn1.Bind(wx.EVT_BUTTON, self.GenerateFormula)

        vbox.Add((-1, 10))

        panel.SetSizer(vbox)


    def SliderUpdate(self, event):
        pos = self.slider.GetValue()
        self.pdfwindow._UpdateScale(self.pdfwindow.initscale + (pos-50.0)/6.)


    def LoadHistory(self):
        histfile = open(globalpath+'/history.fleg', 'r')
        self.history = histfile.readlines()
        for l in self.history:
            self.combohist.Insert(l[:-1],pos=0)
        histfile.close()


    def UpdateHistory(self):
        if self.combohist.GetValue() != self.tc2.GetValue():
            histfile = open(globalpath+'/history.fleg', 'w')
            self.history.append(self.tc2.GetValue()+"\n")
            if len(self.history) > 15:
                del self.history[0]
                self.combohist.Delete(15)
            for h in self.history:
                histfile.write(h)
            histfile.close()
            self.combohist.Insert(self.tc2.GetValue(),pos=0)


    def TakeFormulaFromHist(self, event):
        self.tc2.SetValue(self.combohist.GetValue())


    def GenerateFormula(self, event):
        self.formula = self.tc2.GetValue() #r"\frac{\alpha}{2}"
        tempfile = open(globalpath+"/temp.tex",'w')
        tempfile.write(r"\documentclass{article} \begin{document} \pagestyle{empty} \[" + self.formula + r"\] \end{document}")
        tempfile.close()
        subprocess.Popen("pdflatex --output-directory "+globalpath+" "+globalpath+"/temp.tex", shell=True)
        subprocess.call("pdfcrop "+globalpath+"/temp.pdf "+globalpath+"/temp.pdf", shell=True)

        if self.combobox.GetValue() == "svg":
            subprocess.call("pdf2svg "+globalpath+"/temp.pdf "+globalpath+"/temp.svg", shell=True)

        if self.combobox.GetValue() == "png":
            subprocess.call("convert -density 3000 "+globalpath+"/temp.pdf "+globalpath+"/temp.png", shell=True)

        self.pdfwindow.filetype = self.combobox.GetValue()
        self.slider.Enable()
        self.slider.SetValue(50)
        self.pdfwindow.LoadDocument(globalpath+"/temp.pdf")
        self.pdfwindow.Refresh()
        self.pdfwindow.SetFocus()
        self.UpdateHistory()


if __name__ == '__main__':

    app = wx.App()
    FLEG(None, title='FLEG')
    app.MainLoop()
