import re
from openalea.plantgl.scenegraph import Polyline,Polyline2D,BezierCurve2D,NurbsCurve2D
from openalea.plantgl.math import Vector3,Vector2,norm
from svg_element import SVGElement

#to read svg paths
#I cannot for the moment repeat implicitly a command
#norm : http://www.w3.org/TR/SVG/paths.html
sep=r"\s*,?\s*"
coord=r"([-]?\d+[.]?\d*)"
point=coord+sep+coord

mM=sep+"([mM])"+sep+point
zZ=sep+"([zZ])"
#staight lines
lL=sep+"([lL])"+sep+point
hH=sep+"([hH])"+sep+coord
vV=sep+"([vV])"+sep+coord
#curves
cC=sep+"([cC])"+sep+point+sep+point+sep+point
sS=sep+"([sS])"+sep+point+sep+point
qQ=sep+"([qQ])"+sep+point+sep+point
tT=sep+"([tT])"+sep+point
aA=sep+"([aA])"+sep+point+sep+coord+sep+"([01])"+sep+"([01])"+sep+point

readpath=re.compile("|".join([mM,zZ,lL,hH,vV,cC,sS,qQ,tT,aA]))


class SVGPathCommand (object) :
	"""
	a abstraction of svg path commands
	voir : http://wiki.svg.org/Path
	"""
	def __init__ (self, typ) :
		self._type=typ
		self._params=[]
	
	def type (self) :
		return self._type
	
	def parameters (self) :
		return iter(self._params)
	
	def append (self, val) :
		self._params.append(val)

class SVGPath (SVGElement) :
	"""
	a abstraction of svg path
	voir : http://wiki.svg.org/Path
	"""
	def __init__ (self, parent=None, svgid=None) :
		SVGElement.__init__(self,parent,svgid)
		self._commands=[]
	
	def commands (self) :
		return iter(self._commands)
	
	def append (self, cmd_typ, cmd_args=[]) :
		cmd=SVGPathCommand(cmd_typ)
		for arg in cmd_args :
			cmd.append(arg)
		self._commands.append(cmd)
	def is_closed (self) :
		for command in self.commands() :
			if command.type().lower()=='z' :
				return True
		return False
	
	def from_string (self, command_str) :
		self._commands=[]
		ref_point=Vector2()
		for match in readpath.finditer(command_str) :
			cmd=[v for v in match.groups() if v is not None]
			typ=cmd[0]
			pth_cmd=SVGPathCommand(typ)
			if typ=='M' :
				svgx,svgy=(float(val) for val in cmd[1:])
				pos=Vector2(*self.real_pos(svgx,svgy))
				pth_cmd.append(pos)
				ref_point=pos
			elif typ=='m' :
				svgdx,svgdy=(float(val) for val in cmd[1:])
				vec=Vector2(*self.real_vec(svgdx,svgdy))
				pth_cmd.append(vec)
				ref_point+=vec
			elif typ in ('Z','z') :
				pass
			elif typ=='L' :
				svgx,svgy=(float(val) for val in cmd[1:])
				pos=Vector2(*self.real_pos(svgx,svgy))
				pth_cmd.append(pos)
				ref_point=pos
			elif typ=='l' :
				svgdx,svgdy=(float(val) for val in cmd[1:])
				vec=Vector2(*self.real_vec(svgdx,svgdy))
				pth_cmd.append(vec)
				ref_point+=vec
			elif typ in ('H','h') :
				svgdx,=(float(val) for val in cmd[1:])
				vec=Vector2(*self.real_vec(svgdx,0))
				pth_cmd.append(vec)
				ref_point+=vec
			elif typ in ('V','v') :
				svgdy,=(float(val) for val in cmd[1:])
				vec=Vector2(*self.real_vec(0,svgdy))
				pth_cmd.append(vec)
				ref_point+=vec
			elif typ=='C' :
				svgx1,svgy1,svgx2,svgy2,svgx,svgy=(float(val) for val in cmd[1:])
				v1=Vector2(*self.real_pos(svgx1,svgy1))
				v2=Vector2(*self.real_pos(svgx2,svgy2))
				pos=Vector2(*self.real_pos(svgx,svgy))
				pth_cmd.append(v1)
				pth_cmd.append(v2)
				pth_cmd.append(pos)
				ref_point=pos
			elif typ=='c' :
				svgx1,svgy1,svgx2,svgy2,svgdx,svgdy=(float(val) for val in cmd[1:])
				v1=Vector2(*self.real_vec(svgx1,svgy1))
				v2=Vector2(*self.real_vec(svgx2,svgy2))
				vec=Vector2(*self.real_vec(svgdx,svgdy))
				pth_cmd.append(v1)
				pth_cmd.append(v2)
				pth_cmd.append(vec)
				ref_point+=vec
			elif typ=='S' :
				svgx2,svgy2,svgx,svgy=(float(val) for val in cmd[1:])
				v2=Vector2(*self.real_pos(svgx2,svgy2))
				pos=Vector2(*self.real_pos(svgx,svgy))
				pth_cmd.append(v2)
				pth_cmd.append(pos)
				ref_point=pos
			elif typ=='s' :
				svgx2,svgy2,svgdx,svgdy=(float(val) for val in cmd[1:])
				v2=Vector2(*self.real_vec(svgx2,svgy2))
				vec=Vector2(*self.real_vec(svgdx,svgdy))
				pth_cmd.append(v2)
				pth_cmd.append(vec)
				ref_point+=vec
			elif typ=='Q' :
				svgx1,svgy1,svgx,svgy=(float(val) for val in cmd[1:])
				v1=Vector2(*self.real_pos(svgx1,svgy1))
				pos=Vector2(*self.real_pos(svgx,svgy))
				pth_cmd.append(v1)
				pth_cmd.append(pos)
				ref_point=pos
			elif typ=='q' :
				svgx1,svgy1,svgdx,svgdy=(float(val) for val in cmd[1:])
				v1=Vector2(*self.real_vec(svgx1,svgy1))
				vec=Vector2(*self.real_vec(svgdx,svgdy))
				pth_cmd.append(v1)
				pth_cmd.append(vec)
				ref_point+=vec
			elif typ=='T' :
				svgx,svgy=(float(val) for val in cmd[1:])
				pos=Vector2(*self.real_pos(svgx,svgy))
				pth_cmd.append(pos)
				ref_point=pos
			elif typ=='t' :
				svgdx,svgdy=(float(val) for val in cmd[1:])
				vec=Vector2(*self.real_vec(svgdx,svgdy))
				pth_cmd.append(vec)
				ref_point+=vec
			else :
				raise NotImplementedError("path command type not recognized : % s" % typ)
			self._commands.append(pth_cmd)
	
	def to_string (self) :
		raise NotImplementedError
		ref_point=Vector3()
		path_txt=""
		for command in self.commands() :
			typ=command.type()
			if typ=='M' :
				pos,=command.parameters()
				x,y,z=svgscene.svg_pos(*pos)
				path_txt+="M %f %f" % (x,y)
				ref_point=pos
			elif typ=='m' :
				vec,=command.parameters()
				dx,dy,dz=svgscene.svg_vector(*vec)
				path_txt+="m %f %f" % (x,y)
				ref_point=ref_point+vec
			elif typ in ('Z','z') :
				path_txt+="%s" % typ
			elif typ=='L' :
				pos,=command.parameters()
				x,y,z=svgscene.svg_pos(*pos)
				path_txt+="L %f %f" % (x,y)
				ref_point=pos
			elif typ=='l' :
				vec,=command.parameters()
				dx,dy,dz=svgscene.svg_vector(*vec)
				path_txt+="l %f %f" % (dx,dy)
				ref_point=ref_point+vec
			elif typ in ('H','h') :
				vec,=command.parameters()
				dx,dy,dz=svgscene.svg_vector(*vec)
				path_txt+="%s %f" % (typ,dx)
				ref_point=ref_point+vec
			elif typ in ('V','v') :
				vec,=command.parameters()
				dx,dy,dz=svgscene.svg_vector(*vec)
				path_txt+="%s %f" % (typ,dy)
				ref_point=ref_point+vec
			elif typ=='C' :
				v1,v2,pos=command.parameters()
				x1,y1,z1=svgscene.svg_pos(*v1)
				x2,y2,z2=svgscene.svg_pos(*v2)
				x,y,z=svgscene.svg_pos(*pos)
				path_txt+="C %f %f %f %f %f %f" % (x1,y1,x2,y2,x,y)
				ref_point=pos
			elif typ=='c' :
				v1,v2,vec=command.parameters()
				x1,y1,z1=svgscene.svg_vector(*v1)
				x2,y2,z2=svgscene.svg_vector(*v2)
				dx,dy,dz=svgscene.svg_vector(*vec)
				path_txt+="c %f %f %f %f %f %f" % (x1,y1,x2,y2,dx,dy)
				ref_point=ref_point+vec
			elif typ=='S' :
				v2,pos=command.parameters()
				x2,y2,z2=svgscene.svg_pos(*v2)
				x,y,z=svgscene.svg_pos(*pos)
				path_txt+="S %f %f %f %f" % (x2,y2,x,y)
				ref_point=pos
			elif typ=='s' :
				v2,vec=command.parameters()
				x2,y2,z2=svgscene.svg_vector(*v2)
				dx,dy,dz=svgscene.svg_vector(*vec)
				path_txt+="s %f %f %f %f" % (x2,y2,dx,dy)
				ref_point=ref_point+vec
			elif typ=='Q' :
				v1,pos=command.parameters()
				x1,y1,z1=svgscene.svg_pos(*v1)
				x,y,z=svgscene.svg_pos(*pos)
				path_txt+="Q %f %f %f %f" % (x1,y1,x,y)
				ref_point=pos
			elif typ=='q' :
				v1,vec=command.parameters()
				x1,y1,z1=svgscene.svg_vector(*v1)
				dx,dy,dz=svgscene.svg_vector(*vec)
				path_txt+="q %f %f %f %f" % (x1,y1,dx,dy)
				ref_point=ref_point+vec
			elif typ=='T' :
				pos,=command.parameters()
				x,y,z=svgscene.svg_pos(*pos)
				path_txt+="T %f %f" % (x,y)
				ref_point=pos
			elif typ=='t' :
				vec,=command.parameters()
				dx,dy,dz=svgscene.svg_vector(*vec)
				path_txt+="t %f %f" % (dx,dy)
				ref_point=ref_point+vec
			else :
				raise NotImplementedError("path command type not recognized : % s" % typ)
		return path_txt
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self, svgnode) :
		SVGElement.load(self,svgnode)
		path_txt=svgnode.getAttribute("d")
		self.from_string(path_txt)
	
	def save (self, svgnode) :
		SVGElement.save(self,svgnode)
		self.set_node_type("path")
		path_txt=self.to_string()
		svgnode.setAttribute("d",path_txt)
	
	##############################################
	#
	#		pgl interface
	#
	##############################################
	def polyline_ctrl_points (self) :
		"""
		return a list of control points
		"""
		ref_point=Vector3()
		for command in self.commands() :
			typ=command.type()
			if typ=='M' :
				pos,=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='m' :
				vec,=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ in ('Z','z') :
				pass
			elif typ=='L' :
				pos,=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='l' :
				vec,=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ in ('H','h') :
				vec,=command.parameters()
				ref_point+=vec
				yield ref_point
			elif typ in ('V','v') :
				vec,=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ=='C' :
				v1,v2,pos=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='c' :
				v1,v2,vec=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ=='S' :
				v2,pos=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='s' :
				v2,vec=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ=='Q' :
				v1,pos=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='q' :
				v1,vec=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ=='T' :
				pos,=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='t' :
				vec,=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			else :
				raise NotImplementedError("path command type not recognized : % s" % typ)
	
	def nurbs_ctrl_points (self) :
		"""
		return a list of control points from this path
		"""
		ref_point=Vector2(0,0)
		for command in self.commands() :
			typ=command.type()
			if typ=='M' :
				ref_point,=command.parameters()
				yield ref_point
			elif typ=='m' :
				vec,=command.parameters()
				ref_point==vec
				yield ref_point
			elif typ in ('Z','z') :
				pass
			elif typ=='L' :
				ref_point,=command.parameters()
				yield ref_point
			elif typ=='l' :
				vec=command.parameters()
				ref_point+=vec
				yield ref_point
			elif typ=='C' :
				v1,v2,ref_point=command.parameters()
				yield v1
				yield v2
				yield ref_point
			elif typ=='c' :
				v1,v2,vec=command.parameters()
				yield ref_point+v1
				yield ref_point+v2
				ref_point+=vec
				yield ref_point
			else :
				raise UserWarning("command not available for nurbs %s" % typ)
	
	def polyline (self) :
		return Polyline2D(list(self.polyline_ctrl_points()))
	
	def nurbs (self, ctrl_pts=None, degree=3, uniform=False) :
		#control point
		if ctrl_pts is None :
			ctrl_pts=list(self.nurbs_ctrl_points())
		#knot vector
		nb_pts=len(ctrl_pts)
		nb_arc=(nb_pts-1)/degree
		nb_knots=degree+nb_pts
		p=0.
		param=[p]
		for i in xrange(nb_arc) :
			if uniform :
				p+=1
			else :
				p+=norm(ctrl_pts[degree*i]-ctrl_pts[degree*(i+1)])
			param.append(p)
		kv=[param[0]]
		for p in param :
			for j in xrange(degree) :
				kv.append(p)
		kv.append(param[-1])
		#curve
		return NurbsCurve2D([Vector3(v[0],v[1],1.) for v in ctrl_pts],kv,degree,60)
	
	def to_pgl2D (self,  pglshape) :
		geom=self.polyline()
		pglshape.geometry=geom
		return SVGElement.to_pgl2D(self,pglshape)
	
	def to_pgl3D (self, pglshape) :
		geom=self.polyline()
		pglshape.geometry=geom
		return SVGElement.to_pgl3D(self,pglshape)


class SVGConnector (SVGPath) :
	def __init__ (self, parent=None, svgid=None) :
		SVGPath.__init__(self,parent,svgid)
		self._source=None
		self._target=None
	
	def load (self, svgnode) :
		SVGPath.load(self,svgnode)
		self._source=str(svgnode.getAttribute("inkscape:connection-start"))[1:]
		self._target=str(svgnode.getAttribute("inkscape:connection-end"))[1:]
	
	def save (self, svgnode) :
		SVGPath.save(self,svgnode)
		svgnode.setAttribute("inkscape:connection-start","#%s" % self._source)
		svgnode.setAttribute("inkscape:connection-end","#%s" % self._target)
		svgnode.setAttribute("inkscape:connection-type","polyline")

