# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ContrastHomogenizer
                                 A QGIS plugin
 Applies the contrast enhancement parameters of the selected layer to all visible layers
                             -------------------
        begin                : 2013-03-07
        copyright            : (C) 2012-2016, CS Systèmes d'Information (CS SI)
                               (C) 2019, Alexia Mondot
        contact              : Alexia Mondot <contact@mondot.fr>
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ContrastHomogenizer class from file ContrastHomogenizer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .contrastHomogenizer import ContrastHomogenizer
    return ContrastHomogenizer(iface)
