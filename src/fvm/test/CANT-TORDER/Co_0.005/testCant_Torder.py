#!/usr/bin/env python

import sys
sys.setdlopenflags(0x100|0x2)

import fvm
import fvm.fvmbaseExt as fvmbaseExt
import fvm.importers as importers
fvm.set_atype('double')

import math

if fvm.atype == 'double':
    import fvm.models_atyped_double as models
    import fvm.exporters_atyped_double as exporters
elif fvm.atype == 'tangent':
    import fvm.models_atyped_tangent_double as models
    import fvm.exporters_atyped_tangent_double as exporters

from FluentCase import FluentCase
from optparse import OptionParser

#fvmbaseExt.enableDebug("cdtor")

fileBase = None
fileBase = "/scratch/prism/shankha/memosa/src/fvm/test/CANT-TORDER/Co_0.005/cbeam7"
#fileBase = "/home/sm/app-memosa/src/fvm/test/cav32"
#fileBase = "/home/sm/a/data/wj"

def usage():
    print "Usage: %s filebase [outfilename]" % sys.argv[0]
    print "Where filebase.cas is a Fluent case file."
    print "Output will be in filebase-prism.dat if it is not specified."
    sys.exit(1)

def advanceUnsteady(smodel,meshes,geomFields,structureFields,globalTime,nTimeSteps):
    fileName = fileBase + "data.txt"
    file = open(fileName,"w")
    mesh=meshes[0]
    deformation =  structureFields.deformation[mesh.getCells()].asNumPyArray()
    for i in range(0,nTimeSteps):        
        if i<300000:
            # right
            bcID = 4
            if bcID in bcMap:
                bc = smodel.getBCMap()[bcID]
                bc.bcType = 'SpecifiedDistForce'
                bc['specifiedXDistForce']=0
                bc['specifiedYDistForce']=-1000*((i+1)/300000.)
                bc['specifiedZDistForce']=0
        if i>=300000:
            # right
            bcID = 4
            if bcID in bcMap:
                bc = smodel.getBCMap()[bcID]
                bc.bcType = 'SpecifiedDistForce'
                bc['specifiedXDistForce']=0
                bc['specifiedYDistForce']=-1000.
                bc['specifiedZDistForce']=0
        smodel.advance(numIterationsPerStep)
        if ((i%4000.)==0.):
            file.write(" %e " % globalTime)
            file.write(" %e " % deformation[400][0])
            file.write(" %e " % deformation[400][1])
            file.write("\n")
        globalTime += timeStep
        print 'advancing to time %e at iteration %i' % (globalTime,i)
        smodel.updateTime()
    file.close()

def createBVFields(geomFields,meshes,id):
    fy = fvmbaseExt.Field('bvy')

    mesh = meshes[0]
    vol = geomFields.volume[mesh.getCells()]
    
    for mesh in meshes:
        fgs = mesh.getBoundaryGroups()
        for fg in fgs:
            if fg.id==id:
                nFaces = fg.site.getCount()
                forceY = vol.newSizedClone(nFaces)
                forceYa = forceY.asNumPyArray()
                xf =  geomFields.coordinate[fg.site].asNumPyArray()
                
                pot_top=10.0
                pot_bot=0.0
                len=400.e-6
                gap=3.75e-6
                perm=8.8542e-12
                dpot=(pot_top-pot_bot)/gap
                sigmat=-perm*dpot
                felec=(sigmat*sigmat)*len/(2.*perm)
                felecPerUnitLen=-felec/(len)
                print '\n electric force per unit length = %f' % (felecPerUnitLen)
                
                for i in range(0,nFaces):
                    forceYa[i]=felecPerUnitLen
                    print '\n force %f %f %f' % (xf[i,0],xf[i,1],forceYa[i])
                fy[fg.site] = forceY
                return fy

# change as needed

# map between fvm, tecplot, and xdmf types
etype = {
    'tri' : 1,
    'quad' : 2,
    'tetra' : 3,
    'hexa' : 4
        }
tectype = {
    'tri' : 'FETRIANGLE',
    'quad' : 'FEQUADRILATERAL',
    'tetra' : 'FETETRAHEDRON',
    'hexa' : 'FEBRICK'
        }

def dumpTecplotFile(nmesh, meshes, geomFields, mtype):
    #cell sites
    cellSites = []
    for n in range(0,nmesh):
        cellSites.append( meshes[n].getCells() )
#     print "cellSites[", n, "].getCount = ", cellSites[n].getCount()
        
    #face sites
    faceSites = []
    for n in range(0,nmesh):
        faceSites.append( meshes[n].getFaces() )
        
    #node sites
    nodeSites = []
    for n in range(0,nmesh):
        nodeSites.append( meshes[n].getNodes() )
        
    #get connectivity (faceCells)
    faceCells = []
    for n in range(0,nmesh):
        faceCells.append( meshes[n].getConnectivity( faceSites[n], cellSites[n] ) )
        
    #get connectivity ( cellNodes )
    cellNodes = []
    for n in range(0,nmesh):
        cellNodes.append( meshes[n].getCellNodes() )
        
    #get Volume as array
    volumes = []
    for n in range(0,nmesh):
        volumes.append( geomFields.volume[cellSites[n]].asNumPyArray() )
    
    
    cellCentroids =[]
    for n in range(0,nmesh):
        cellCentroids.append( geomFields.coordinate[cellSites[n]].asNumPyArray() )
        
    defFields = []
    for n in range(0,nmesh):
        defFields.append( structureFields.deformation[cellSites[n]].asNumPyArray() )

    tractionXFields = []
    for n in range(0,nmesh):
        tractionXFields.append( structureFields.tractionX[cellSites[n]].asNumPyArray() )
        
    coords = []
    for n in range(0,nmesh):
        coords.append( geomFields.coordinate[nodeSites[n]].asNumPyArray() )
#     print "shape( coords[", n, "] ) = ", shape( coords[n] )

    f = open("tecplot_wbar1.dat","w")
    f.write("Title = \" tecplot file for 2D Cavity problem \" \n")
    f.write("variables = \"x\", \"y\", \"z\", \"defX\", \"defY\", \"sigmaXX\", \"sigmaXY\", \"sigmaYY\", \"cellCentroidY\" \n")
    for n in range(0,nmesh):
        title_name = "nmesh%s" % n
        ncell  = cellSites[n].getSelfCount()
        nnode  = nodeSites[n].getCount()
        f.write("Zone T = \"%s\" N = %s E = %s DATAPACKING = BLOCK, VARLOCATION = ([4-9]=CELLCENTERED), ZONETYPE=%s\n" %
                (title_name,  nodeSites[n].getCount(), ncell, tectype[mtype]))
        #write x
        for i in range(0,nnode):
            f.write(str(coords[n][i][0])+"    ")
            if ( i % 5 == 4 ):
                f.write("\n")
        f.write("\n")
                
        #write y
        for i in range(0,nnode):
            f.write(str(coords[n][i][1])+"    ")
            if ( i % 5 == 4 ):
                f.write("\n")
        f.write("\n")

        #write z
        for i in range(0,nnode):
            f.write(str(coords[n][i][2])+"    ")
            if ( i % 5 == 4 ):
                f.write("\n")
        f.write("\n")

        #write defX
        for i in range(0,ncell):
            f.write(str(defFields[n][i][0]) + "    ")
            if ( i % 5  == 4 ):
                f.write("\n")
        f.write("\n")

        #write defY
        for i in range(0,ncell):
            f.write(str(defFields[n][i][1]) + "    ")
            if ( i % 5  == 4 ):
                f.write("\n")
        f.write("\n")

        #write sigmaXX
        for i in range(0,ncell):
            f.write(str(tractionXFields[n][i][0]) + "    ")
            if ( i % 5  == 4 ):
                f.write("\n")
        f.write("\n")

        #write sigmaXY
        for i in range(0,ncell):
            f.write(str(tractionXFields[n][i][1]) + "    ")
            if ( i % 5  == 4 ):
                f.write("\n")
        f.write("\n")
                                                    
        #write sigmaYY
        for i in range(0,ncell):
            f.write(str(tractionXFields[n][i][2]) + "    ")
            if ( i % 5  == 4 ):
                f.write("\n")
        f.write("\n")
                                                                    
        #write velX
        for i in range(0,ncell):
            f.write( str(cellCentroids[n][i][1]) + "    ")
            if ( i % 5  == 4 ):
                f.write("\n")
        f.write("\n")

        #connectivity
        for i in range(0,ncell):
            nnodes_per_cell = cellNodes[n].getCount(i)
            for node in range(0,nnodes_per_cell):
                f.write( str(cellNodes[n](i,node)+1) + "     ")
            f.write("\n")
        f.write("\n")
    f.close()

parser = OptionParser()
parser.set_defaults(type='quad')
parser.add_option("--type", help="'quad'[default], 'tri', 'hexa', or 'tetra'")
parser.add_option("--xdmf", action='store_true', help="Dump data in xdmf")
parser.add_option("--time","-t",action='store_true',help="Print timing information.")
(options, args) = parser.parse_args()

outfile = None
if __name__ == '__main__' and fileBase is None:
    if len(sys.argv) < 2:
        usage()
    fileBase = sys.argv[1]
    if len(sys.argv) == 3:
        outfile = sys.argv[2]

if outfile == None:
    outfile = fileBase+"-prism.dat"
    
reader = FluentCase(fileBase+".cas")

#import debug
reader.read();

meshes = reader.getMeshList()
mesh = meshes[0]
nmesh = 1
   
import time
t0 = time.time()

geomFields =  models.GeomFields('geom')
metricsCalculator = models.MeshMetricsCalculatorA(geomFields,meshes)

metricsCalculator.init()

cells = mesh.getCells()

rho = 7854.0
E = 2.0*math.pow(10,11)
nu = 0.31

if fvm.atype == 'tangent':
    metricsCalculator.setTangentCoords(0,7,1)

structureFields =  models.StructureFields('structure')
smodel = models.StructureModelA(geomFields,structureFields,meshes)

bcMap = smodel.getBCMap()

#left
bcID = 6
if bcID in bcMap:
    bc = smodel.getBCMap()[bcID]
    bc.bcType = 'SpecifiedDeformation'
    bc['specifiedXDeformation']=0
    bc['specifiedYDeformation']=0
    bc['specifiedZDeformation']=0
                    
#top 
bcID = 5
if bcID in bcMap:
    bc = smodel.getBCMap()[bcID]
    bc.bcType = 'SpecifiedTraction'
    bc['specifiedXXTraction']=0
    bc['specifiedXYTraction']=0
    bc['specifiedXZTraction']=0
    bc['specifiedYXTraction']=0
    bc['specifiedYYTraction']=0
    bc['specifiedYZTraction']=0
    bc['specifiedZXTraction']=0
    bc['specifiedZYTraction']=0
    bc['specifiedZZTraction']=0

# right
#bcID = 4
#if bcID in bcMap:
#    bc = smodel.getBCMap()[bcID]
#    bc.bcType = 'SpecifiedDistForce'
#    felec=createBVFields(geomFields,meshes,bcID)
#    bc['specifiedXDistForce']=0
#    bc['specifiedYDistForce']=-12.5
#    bc['specifiedZDistForce']=0


#bottom
bcID = 3
if bcID in bcMap:
    bc = smodel.getBCMap()[bcID]
    bc.bcType = 'SpecifiedTraction'
    bc['specifiedXXTraction']=0
    bc['specifiedXYTraction']=0
    bc['specifiedXZTraction']=0
    bc['specifiedYXTraction']=0
    bc['specifiedYYTraction']=0
    bc['specifiedYZTraction']=0
    bc['specifiedZXTraction']=0
    bc['specifiedZYTraction']=0
    bc['specifiedZZTraction']=0

vcMap = smodel.getVCMap()
for i,vc in vcMap.iteritems():
    vc['density'] = rho
    vc['eta'] = E/(2.*(1+nu))
    vc['eta1'] = nu*E/((1+nu)*(1-1.0*nu))

pc = fvmbaseExt.AMG()
pc.verbosity=0
defSolver = fvmbaseExt.BCGStab()
defSolver.preconditioner = pc
defSolver.relativeTolerance = 1e-9
defSolver.absoluteTolerance = 1e-30
defSolver.nMaxIterations = 5000
#defSolver.maxCoarseLevels=20
defSolver.verbosity=0

soptions = smodel.getOptions()
soptions.deformationLinearSolver = defSolver
soptions.deformationTolerance=1.0e-3
soptions.setVar("deformationURF",1.0)
soptions.printNormalizedResiduals=True
soptions.transient=True

numTimeSteps = 16000000
numIterationsPerStep = 1
period = 0.12267
timeStep = 1.e-7
globalTime=0.

# set the timesteps
soptions.setVar('timeStep',timeStep)

"""
if fvm.atype=='tangent':
    vcMap = fmodel.getVCMap()
    for i,vc in vcMap.iteritems():
        print vc.getVar('viscosity')
        vc.setVar('viscosity',(1.7894e-5,1))
"""
cellCoordinate = geomFields.coordinate[cells].asNumPyArray()
#for c in range(0,cells.getSelfCount()):
print 'mid point on right is %e %e' %(cellCoordinate[400][0],cellCoordinate[400][1])

smodel.init()
advanceUnsteady(smodel,meshes,geomFields,structureFields,globalTime,numTimeSteps)

#smodel.getTractionX(mesh)

t1 = time.time()
if outfile != '/dev/stdout':
    print '\nsolution time = %f' % (t1-t0)

#dumpTecplotFile( nmesh, meshes, geomFields, options.type)




