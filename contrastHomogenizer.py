# -*- coding: utf-8 -*-
"""
/***************************************************************************
                        Contrast homogenizer
 A QGIS plugin to apply the dynamic of the current layer to all layers
                              -------------------
        begin                : 2013-03-07
        copyright            : (C) 2012-2013, CS Information Systems, CSSI
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
from PyQt4.QtGui import QAction, QIcon, QMessageBox
from PyQt4.QtCore import QObject, SIGNAL, QFileInfo, QSettings, QCoreApplication, QTranslator, qVersion


from qgis.core import ( QGis,
                        QgsApplication,
                        QgsRasterLayer,
                        QgsSingleBandGrayRenderer,
                        QgsContrastEnhancement,
                        )


# Initialize Qt resources from file resources.py
import resources_rc

#import logging
import logging
# create logger
logger = logging.getLogger('contrastHomogenizer')
logger.setLevel(logging.DEBUG)


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
        """
        Init of the plugin.
        Automatic function to load the plugin
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/contrastHomogenizer"
        # initialize locale
        localePath = ""
        
        if QGis.QGIS_VERSION_INT <= 10900 :
            locale = QSettings().value("locale/userLocale").toString()[0:2]
    
        else :
            locale = QSettings().value("locale/userLocale")[0:2]
    
        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/contrastHomogenizer_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


    def initGui(self):
        """
        Creates action that will start plugin configuration and connects the run method
        """
        # 
        self.action = QAction(
            QIcon(":/plugins/contrastHomogenizer/icon.png"),
            u"Contrast Homogenizer", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Same dynamic to all layers", self.action)


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Same dynamic to all layers", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
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
        
        # if a layer were selected,
        if not layer == None :   
            
            layername = layer.name()
            logger.info( layername )

            # type of layer : raster, vector, other
            typeOfLayer = layer.type()
            logger.debug( "typeOfLayer" + str( typeOfLayer ) )
            
            #take the layer renderer to get the min and max 
            layerRenderer = layer.renderer()
            
            # the layer has to be a raster layer
            if typeOfLayer == 1 :
                #gray band
#                layerRenderer
#                <qgis.core.QgsSingleBandGrayRenderer object at 0x514caf0>
                logger.debug( "raster type : " + str( layer.rasterType()) )
                
                logger.info( layerRenderer )
                
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
        # take the contrast enhancement of the layer threw the renderer
        layerCE = layerRenderer.contrastEnhancement()
        logger.info( layerCE )
        
#                    layerCE
#                    <qgis.core.QgsContrastEnhancement object at 0x514c9e0>
        
        # get computed min and max
        maxCurrent = layerCE.maximumValue()
        minCurrent = layerCE.minimumValue()
        
        logger.info( maxCurrent )
        logger.info( minCurrent )
        
#                    print self.listCanvasLayer

        # for each layer 
        for layerFromList in listCanvasLayer:
            if layerFromList.type() == 1 :
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
#        layerRenderer
#        <qgis.core.QgsMultiBandColorRenderer object at 0x514c9e0>
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

                if layerFromList.type() == 1 :
                    logger.debug( "layer from list is a raster file" )

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

#                        rendererFromList.setRedContrastEnhancement( layerCERed )
#                        rendererFromList.setGreenContrastEnhancement( layerCEGreen  )
#                        rendererFromList.setBlueContrastEnhancement( layerCEBlue )
                        redEnhancement = None
                        if QGis.QGIS_VERSION_INT == 10800:  # for QGIS = 1.8
                            redEnhancement = QgsContrastEnhancement(QgsContrastEnhancement.QgsRasterDataType(dataProvider.dataType(0)))
                        elif QGis.QGIS_VERSION_INT >= 10900:  # for QGIS = 1.9
                            redEnhancement = QgsContrastEnhancement(dataProvider.dataType(1))

                        if redEnhancement :
                            redEnhancement.setMinimumValue( minCurrentRed )
                            redEnhancement.setMaximumValue( maxCurrentRed )
                            redEnhancement.setContrastEnhancementAlgorithm(1)
                            rendererFromList.setRedContrastEnhancement( redEnhancement )

                        greenEnhancement = None
                        if QGis.QGIS_VERSION_INT == 10800:  # for QGIS = 1.8
                            greenEnhancement = QgsContrastEnhancement(QgsContrastEnhancement.QgsRasterDataType(dataProvider.dataType(1)))
                        elif QGis.QGIS_VERSION_INT >= 10900:  # for QGIS = 1.9
                            greenEnhancement = QgsContrastEnhancement(dataProvider.dataType(2))

                        if greenEnhancement :
                            greenEnhancement.setMinimumValue( minCurrentGreen )
                            greenEnhancement.setMaximumValue( maxCurrentGreen )
                            greenEnhancement.setContrastEnhancementAlgorithm(1)
                            rendererFromList.setGreenContrastEnhancement( greenEnhancement )

                        blueEnhancement = None
                        if QGis.QGIS_VERSION_INT == 10800:  # for QGIS = 1.8
                            blueEnhancement = QgsContrastEnhancement(QgsContrastEnhancement.QgsRasterDataType(dataProvider.dataType(2)))
                        elif QGis.QGIS_VERSION_INT >= 10900:  # for QGIS = 1.9
                            blueEnhancement = QgsContrastEnhancement(dataProvider.dataType(3))

                        if blueEnhancement :
                            blueEnhancement.setMinimumValue( minCurrentBlue )
                            blueEnhancement.setMaximumValue( maxCurrentBlue )
                            blueEnhancement.setContrastEnhancementAlgorithm(1)
                            rendererFromList.setBlueContrastEnhancement( blueEnhancement )

                        layerFromList.setCacheImage(None)
                        layerFromList.triggerRepaint()
                        
#                        layerFromListCERed = rendererFromList.redContrastEnhancement()
#                        
#                        print "layerFromListCERed", layerFromListCERed
#                        
#                        layerFromListCEGreen = rendererFromList.greenContrastEnhancement()
#                        layerFromListCEBlue = rendererFromList.blueContrastEnhancement()
#                        
#                        layerFromListCERed.setContrastEnhancementAlgorithm(1)
#                        layerFromListCEGreen.setContrastEnhancementAlgorithm(1)
#                        layerFromListCEBlue.setContrastEnhancementAlgorithm(1)
#                        
#                        layerFromListCERed.setMinimumValue(minCurrentRed)
#                        layerFromListCEGreen.setMinimumValue(minCurrentGreen)
#                        layerFromListCEBlue.setMinimumValue(minCurrentBlue)
#                        
#                        layerFromListCERed.setMaximumValue(maxCurrentRed)
#                        layerFromListCEGreen.setMaximumValue(maxCurrentGreen)
#                        layerFromListCEBlue.setMaximumValue(maxCurrentBlue)
                        
                        
                        
#                        logger.info("min max set")
                        
#                        layerFromListCERed.setContrastEnhancementAlgorithm(1)
#                        layerFromListCEGreen.setContrastEnhancementAlgorithm(1)
#                        layerFromListCEBlue.setContrastEnhancementAlgorithm(1)
#                        
#                        print "red :", layerFromListCERed.contrastEnhancementAlgorithm()
#                        print "green:", layerFromListCEGreen.contrastEnhancementAlgorithm()
#                        print "blue :", layerFromListCEBlue.contrastEnhancementAlgorithm()
#
#                        print "min red:", layerFromListCERed.minimumValue(), "max red:", layerFromListCERed.maximumValue()
#                        print "min green:", layerFromListCEGreen.minimumValue(), "max green:", layerFromListCEGreen.maximumValue()
#                        print "min blue:", layerFromListCEBlue.minimumValue(), "max blue:", layerFromListCEBlue.maximumValue()
#                        
#                        print "contrast enhancement :", layerFromListCERed.contrastEnhancementAlgorithm()
#                        print "contrast enhancement :", layerFromListCEGreen.contrastEnhancementAlgorithm()
#                        print "contrast enhancement :", layerFromListCEBlue.contrastEnhancementAlgorithm()
                        
#                        rendererFromList.setRedContrastEnhancement( layerFromListCERed )
#                        rendererFromList.setGreenContrastEnhancement( layerFromListCEGreen )
#                        rendererFromList.setBlueContrastEnhancement( layerFromListCEBlue )
#                        

        
