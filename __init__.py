# -*- coding: utf-8 -*-
"""
/***************************************************************************
                        Contrast homogenizer
 A QGIS plugin to apply the dynamic of the current layer to all layers
                             -------------------
        begin                : 2013-03-07
        copyright            : (C) 2012-2013, CS Information Systems, CSSI
        contributors         : Alexia Mondot
        email                : alexia.mondot@c-s.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "Contrast homogenizer"


def description():
    return "Applies the contrast enhancement parameters of the selected layer to all visible layers"


def version():
    return "Version 2.1"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "1.8"

def qgisMaximumVersion():
    return "2.9"


def author():
    return "CS Information Systems"


def email():
    return "composants_cs-qgis@vulcain.si.c-s.fr"


def classFactory(iface):
    # load Dynamics class from file ContrastHomogenizer
    from contrastHomogenizer import ContrastHomogenizer
    return ContrastHomogenizer(iface)
