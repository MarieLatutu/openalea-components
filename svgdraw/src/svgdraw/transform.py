# -*- python -*-
#
#       svgdraw: svg library
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

"""
This module defines an svg transformation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

import re

#to read svg transformations or values
#norm : http://www.w3.org/TR/SVG/coords.html#TransformAttribute
sep = r"\s*,?\s*"
digit = r"([-]?\d+[.]?\d*e?[+-]?\d?)"
float_re = re.compile(digit+r"(em)?(ex)?(px)?(pt)?(pc)?(cm)?(mm)?(in)?(\%)?")

matrix_re = re.compile("matrix\("+digit+sep+digit+sep+digit+sep+digit+sep+digit+sep+digit+"\)")
translate_re = re.compile("translate\("+digit+sep+digit+"?\)")
scale_re = re.compile("scale\("+digit+sep+digit+"?\)")

class SVGTransform (object) :
	"""Class to manage SVG transformations.
	
	scaling,translation,rotation
	"""
	def __init__ (self) :
		self._m00 = 1.
		self._m01 = 0.
		self._m10 = 0.
		self._m11 = 1.
		self._t0 = 0.
		self._t1 = 0.
	
	def __str__ (self) :
		return "%.4f %.4f\t%.4f\n%.4f %.4f\t%.4f" % (self._m00,
		                                             self._m01,
		                                             self._t0,
		                                             self._m10,
		                                             self._m11,
		                                             self._t1)
	
	#############################################
	#
	#	vectorial operators
	#
	#############################################
	def apply_to_vec (self, vec) :
		"""Apply the transformation to a given vector.
		"""
		return (self._m00 * vec[0] + self._m01 * vec[1],
		        self._m10 * vec[0] + self._m11 * vec[1])
	
	def apply_to_point (self, point) :
		"""Apply the transformation to a point.
		"""
		vec = self.apply_to_vec(point)
		return (vec[0] + self._t0,vec[1] + self._t1)
	
	#############################################
	#
	#	operators
	#
	#############################################
	def clone (self, transfo) :
		"""Clone the transfo in self.
		"""
		self._m00 = transfo._m00
		self._m01 = transfo._m01
		self._m10 = transfo._m10
		self._m11 = transfo._m11
		
		self._t0 = transfo._t0
		self._t1 = transfo._t1
	
	def __mul__ (self, transfo) :
		"""Composition of transformations.
		
		Add the translation part and
		multiply the matrix part
		"""
		ret = SVGTransform()
		ret._m00 = self._m00 * transfo._m00 + self._m01 * transfo._m10
		ret._m01 = self._m00 * transfo._m01 + self._m01 * transfo._m11
		ret._m10 = self._m10 * transfo._m00 + self._m11 * transfo._m10
		ret._m11 = self._m10 * transfo._m01 + self._m11 * transfo._m11
		
		ret._t0 = self._t0 + transfo._t0
		ret._t1 = self._t1 + transfo._t1
		
		return ret
	
	#############################################
	#
	#	svg serialization
	#
	#############################################
	def read (self, txt) :
		"""Read a txt description of the transfo
		see SVG norm.
		"""
		if "matrix" in txt :
			m00,m10,m01,m11,t0,t1 = (float(val) for val in matrix_re.match(txt).groups() )
			self.clone(matricial(m00,m01,m10,m11,t0,t1) ) #order of coef changed
		elif "translate" in txt :
			xtr,ytr = translate_re.match(txt).groups()
			x = float(xtr)
			if ytr is None :
				y = x
			else :
				y = float(ytr)
			self.clone(translation(x,y) )
		elif "scale" in txt :
			xtr,ytr = scale_re.match(txt).groups()
			x = float(xtr)
			if ytr is None :
				y = x
			else :
				y = float(ytr)
			self.clone(scaling(x,y) )
		elif "rotate" in txt :
			raise NotImplementedError
		elif "skewX" in txt :
			raise NotImplementedError
		elif "skewY" in txt :
			raise NotImplementedError
		else :
			raise UserWarning("don't know how to translate this transformation :\n %s" % txts)
	
	def write (self) :
		"""Return a txt description of the transfo.
		"""
		return "matrix(%f %f %f %f %f %f)" % (self._m00,
		                                      self._m10,
		                                      self._m01,
		                                      self._m11,
		                                      self._t0,
		                                      self._t1)

def translation (dx, dy) :
	"""Return a transformation that translate
	objects. Displacement is dx and dy.
	"""
	transfo = SVGTransform()
	transfo._t0 = dx
	transfo._t1 = dy
	
	return transfo

def scaling (sx, sy = None) :
	"""Return a transformation that scale
	objects. Scaling is sx along x and sy along y.
	"""
	if sy is None :
		sy = sx
	
	transfo = SVGTransform()
	transfo._m00 = sx
	transfo._m11 = sy
	
	return transfo

def rotation (angle) :
	"""Return a transformation that rotate
	objects with an angle 'angle' expressed in radians.
	"""
	transfo = SVGTransform()
	asin = sin(angle)
	acos = cos(angle)
	transfo._m00 = acos
	transfo._m01 = -asin
	transfo._m10 = asin
	transfo._m11 = acos
	
	return transfo

def matricial (m00, m01, m10, m11, t0, t1) :
	"""Return the transformation that correspond
	to this coefficients.
	"""
	transfo = SVGTransform()
	transfo._m00 = m00
	transfo._m01 = m01
	transfo._m10 = m10
	transfo._m11 = m11
	
	transfo._t0 = t0
	transfo._t1 = t1
	
	return transfo


