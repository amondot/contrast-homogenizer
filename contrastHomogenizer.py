# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ContrastHomogenizer
                                 A QGIS plugin
 Applies the contrast enhancement parameters of the selected layer to all visible layers
                              -------------------
        begin                : 2013-03-07
        git sha              : $Format:%H$
        copyright            : (C) 2012-2016, CS Information Systems, CSSI
        contributors         : A. Mondot
        email                : alexia.mondot@c-s.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *    WARNING : the uniformisation for colored image works for             *
 *    qgis-1.9.0-0.+git7e29d7ce.el6.x86_64                                 *
 *    could not test it really on the last version of qgis                 *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, qVersion, QObject, QFileInfo
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox

from qgis.core import ( QgsApplication,
                        QgsContrastEnhancement,
                        )

# Initialize Qt resources from file resources.py
from .resources import *
import os.path

#import logging
import logging
# create logger
logger = logging.getLogger('contrastHomogenizer')
logger.setLevel(logging.INFO)


class ContrastHomogenizer:
    """
    This class allows to apply the dynamic of the current layer to all other layers
    
    Keyword arguments:
        QGIS:
            self.iface   -- qgis interface
            self.canvas  -- qgis map canvas
            self.plugin_dir -- plugin directory
            
    """

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ContrastHomogenizer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Contrast homogenizer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ContrastHomogenizer')
        self.toolbar.setObjectName(u'ContrastHomogenizer')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ContrastHomogenizer', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/contrastHomogenizer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Contrast Homogenizer'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Contrast homogenizer'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """
        This method applies the dynamic.

        Types :
            layerRenderer    --    qgis.core.QgsSingleBandGrayRenderer
            layerCE          --    qgis.core.QgsContrastEnhancement
            layerFromListCE  --    qgis.core.QgsRasterLayer
        """
        #take the current layer
        layer = self.canvas.currentLayer() #QgsMapCanvas
        #take the list of visible layers
        listCanvasLayer = self.canvas.layers()
        
        # if a layer is selected,
        if not layer == None :   
            
            layername = layer.name()
            logger.info( layername )

            # type of layer : raster, vector, other
            typeOfLayer = layer.type()
            logger.debug( "typeOfLayer {}".format(str( typeOfLayer )) )
            
            #take the layer renderer to get the min and max 
            layerRenderer = layer.renderer()
            
            # the layer has to be a raster layer
            if typeOfLayer == 1 :
                # layerRenderer
                # <qgis.core.QgsSingleBandGrayRenderer object at 0x514caf0>
                logger.debug( "raster type : " + str( layer.rasterType()) )
                logger.info( layerRenderer )

                # gray band
                if layer.rasterType() == 0 :
                    self.dynamicsSingleBand(layerRenderer, listCanvasLayer)
                    
                #multiband
                elif layer.rasterType() == 2 :
                    self.dynamicsMultiBand(layerRenderer, listCanvasLayer)
                 
                # refreshing                 
                self.canvas.refresh()    
            # the selected layer is not a raster layer
            else :
                QMessageBox.warning(self.iface.mainWindow(), "Contrast Homogenizer", "Please select a raster layer")
                return False
        #no layer selected
        else :
                QMessageBox.warning(self.iface.mainWindow(), "Contrast Homogenizer", "Please select a raster layer")
                return False
        
        
    def dynamicsSingleBand(self, layerRenderer, listCanvasLayer):
        """
        Applies the dynamic of the selected layer to all single band layers
        :param layerRenderer:
        :param listCanvasLayer:
        :return:
        """
        # take the contrast enhancement of the layer threw the renderer
        layerCE = layerRenderer.contrastEnhancement()
        logger.info( layerCE )
#       layerCE
#       <qgis.core.QgsContrastEnhancement object at 0x514c9e0>
        
        # get computed min and max
        maxCurrent = layerCE.maximumValue()
        minCurrent = layerCE.minimumValue()
        
        logger.info( maxCurrent )
        logger.info( minCurrent )

        # for each layer 
        for layerFromList in listCanvasLayer:
            # which is raster
            if layerFromList.type() == 1 :
                # gray band
                if layerFromList.rasterType() == 0 :
                    #take the layer renderer to set the min and max
                    rendererFromList = layerFromList.renderer()
                    logger.info( rendererFromList )
                    
                    layerFromListCE = rendererFromList.contrastEnhancement()
                    logger.info( layerFromListCE )
                    
                    layerFromListCE.setMinimumValue(minCurrent)
                    layerFromListCE.setMaximumValue(maxCurrent)
                    layerFromList.setCacheImage(None)
                    layerFromList.triggerRepaint()



    def dynamicsMultiBand(self, layerRenderer, listCanvasLayer):
        """
        Applies the dynamic of the selected layer to all multi band layers
        :param layerRenderer:
        :param listCanvasLayer:
        :return:
        """
#       layerRenderer
#       <qgis.core.QgsMultiBandColorRenderer object at 0x514c9e0>
        layerCERed = layerRenderer.redContrastEnhancement()
        layerCEGreen = layerRenderer.greenContrastEnhancement()
        layerCEBlue = layerRenderer.blueContrastEnhancement()


        if layerCERed and layerCEGreen and layerCEBlue:
            #set stretch to min max
            layerCERed.setContrastEnhancementAlgorithm(1)
            layerCEGreen.setContrastEnhancementAlgorithm(1)
            layerCEBlue.setContrastEnhancementAlgorithm(1)

            logger.debug( "red :" + str( layerCERed.contrastEnhancementAlgorithm() ))
            logger.debug( "green:" + str( layerCEGreen.contrastEnhancementAlgorithm() ))
            logger.debug( "blue :" + str( layerCEBlue.contrastEnhancementAlgorithm() ))

            #get the min and max of RGB bands
            maxCurrentRed = layerCERed.maximumValue()
            minCurrentRed = layerCERed.minimumValue()

            logger.debug( "min red:" + str( minCurrentRed ) + "max red:" + str( maxCurrentRed ) )

            maxCurrentGreen = layerCEGreen.maximumValue()
            minCurrentGreen = layerCEGreen.minimumValue()

            logger.debug( "min green:" + str( minCurrentGreen ) + "max green:" + str( maxCurrentGreen ) )

            maxCurrentBlue = layerCEBlue.maximumValue()
            minCurrentBlue = layerCEBlue.minimumValue()

            logger.debug( "min blue:" + str( minCurrentBlue ) + "max blue:" + str( maxCurrentBlue ) )

            # for each layer
            logger.debug( "there are" + str( len(listCanvasLayer) ) + " layers in the canvas" )
            for layerFromList in listCanvasLayer:
                logger.debug( "layer from list name :" + str( layerFromList.name() ) )

                # which is raster
                if layerFromList.type() == 1 :
                    logger.debug( "layer from list is a raster file" )

                    # which is multi
                    if layerFromList.rasterType() == 2 :
                        logger.debug( "multiband file" )

                        dataProvider = layerFromList.dataProvider()
                        #take the layer renderer to set the min and max
                        rendererFromList = layerFromList.renderer()
                        #<qgis.core.QgsMultiBandColorRenderer object at 0x3f8a8d0>
                        logger.debug( "renderer from list" + str( rendererFromList ) )

                        logger.debug( "green band" + str( rendererFromList.greenBand() ) )
                        logger.debug( "blue band" + str( rendererFromList.blueBand() ) )
                        logger.debug( "red band" + str( rendererFromList.redBand() ) )

                        logger.info( rendererFromList )

                        redEnhancement = None
                        redEnhancement = QgsContrastEnhancement(dataProvider.dataType(1))

                        if redEnhancement:
                            redEnhancement.setMinimumValue(minCurrentRed)
                            redEnhancement.setMaximumValue(maxCurrentRed)
                            redEnhancement.setContrastEnhancementAlgorithm(1)
                            rendererFromList.setRedContrastEnhancement( redEnhancement )

                        greenEnhancement = None
                        greenEnhancement = QgsContrastEnhancement(dataProvider.dataType(2))

                        if greenEnhancement:
                            greenEnhancement.setMinimumValue(minCurrentGreen)
                            greenEnhancement.setMaximumValue(maxCurrentGreen)
                            greenEnhancement.setContrastEnhancementAlgorithm(1)
                            rendererFromList.setGreenContrastEnhancement( greenEnhancement )

                        blueEnhancement = None
                        blueEnhancement = QgsContrastEnhancement(dataProvider.dataType(3))

                        if blueEnhancement:
                            blueEnhancement.setMinimumValue(minCurrentBlue)
                            blueEnhancement.setMaximumValue(maxCurrentBlue)
                            blueEnhancement.setContrastEnhancementAlgorithm(1)
                            rendererFromList.setBlueContrastEnhancement( blueEnhancement )

                        layerFromList.setCacheImage(None)
                        layerFromList.triggerRepaint()

