#!/usr/bin/env python

import sys
import pdb

import fvm
import fvm.fvmbaseExt as fvmbaseExt
fvm.set_atype('double')
import fvm.importers as importers
import fvm.exporters_atyped_double as exporters
from mpi4py import MPI


import math
from FluidStructure import *

atype = 'double'
#atype = 'tangent'

from FluentCase import FluentCase

#fvmbaseExt.enableDebug("cdtor")

fileBase = None
numIterationsPerStep = 20
#mpm number of steps shoul numTimeSteps-1
numTimeSteps = 2 
fileBase = "/home/yildirim/memosa/src/fvm/test/"

vFile = open(fileBase + "velocity-fullbeam-test.out","w")
pFile = open(fileBase + "pIntegral-fullbeam-new.out","w")
#mFile = open(fileBase + "test-momIntegral.out","w")

def usage():
    print "Usage: %s filebase" % sys.argv[0]
    print "Where filebase.cas is a Fluent case file."
    print "Output will be in filebase-prism.dat "
    sys.exit(1)

def advance(fmodel,niter):
    fmodel.advance(niter)
    """
    for i in range(0,niter):
        try:
            fmodel.advance(1)
        except KeyboardInterrupt:
            break
    """
    
frequency = 114415.0
#timeStep = 1.0/(frequency*100) *1.0e+3
timeStep = 2.0e-02
globalTime=0

def advanceUnsteady(fmodel, meshes, globalTime, nTimeSteps,  mpm_fvm):    
    #pdb.set_trace()
   
    for i in range(0,nTimeSteps):
        print "ntimesteps = ", str(i)
        globalTime += timeStep 
	mpm_fvm.couplingInit(timeStep)
        mpm_fvm.acceptMPM( i ) 
	print "KKKKKKKKKKKKKKKKKKKKKKKKABBBBBBBBBBBBBBBBBBUUULLLLLLLLLL EDILDI" 
        #v = 0.001*math.cos(2.0*math.pi * frequency * globalTime)
	###fvmbaseExt.CellMark_Impl(mesh0, geomFields, fileBase, octree, solid, option)	

        ###metricsCalculator.computeIBInterpolationMatrices(mpm_fvm.particleSite())

        ###metricsCalculator.computeIBandSolidInterpolationMatrices(mpm_fvm.particleSite())
             
        ###fmodel.computeIBFaceVelocity(mpm_fvm.particleSite())

        ###fmodel.computeIBandSolidVelocity(mpm_fvm.particleSite())

        nsweep = int(2)
        mpm_fvm.updateMPM( i )

        #advance(fmodel,numIterationsPerStep)

        #pI = fmodel.getPressureIntegralonIBFaces(mesh0)
        #mI = fmodel.getMomentumFluxIntegralonIBFaces(mesh0)
               
        #vFile.write("%e\t%e\n" % (globalTime,v))
        #pFile.write("%e\t%e\t%e\t%e\n" % (globalTime, pI[0], pI[1], pI[2]))
        #mFile.write("%e\t%e\t%e\t%e\n" % (globalTime, mI[0], mI[1], mI[2]))
        
        
        print 'advancing to time %e' % globalTime
        fmodel.updateTime()
    
# change as needed

if __name__ == '__main__' and fileBase is None:
    if len(sys.argv) != 2:
        usage()

    fileBase = sys.argv[1]


filename = fileBase+"fvm_coupling_hexa10x4x4_80x32x32.cas"
#filename = fileBase+"fvm_coupling_hexa10x4x4_120x48x48.cas"
#filename = fileBase+"fvm_coupling_hexa10x4x4_160x64x64.cas"

reader = FluentCase(filename)
print "reading %s", filename

#import debug
reader.read();


meshes = reader.getMeshList()

mesh0 = meshes[0]

import time
t0 = time.time()

geomFields =  fvm.models.GeomFields('geom')
metricsCalculator = fvm.models.MeshMetricsCalculatorA(geomFields,meshes)

metricsCalculator.init()

flowFields =  fvm.models.FlowFields('flow')

fmodel = fvm.models.FlowModelA(geomFields,flowFields,meshes)

reader.importFlowBCs(fmodel)
#fmodel.printBCs()

momSolver = fvmbaseExt.AMG()
momSolver.relativeTolerance = 1e-1
momSolver.absoluteTolerance = 1e-25
#momSolver.nMaxIterations = 20
#momSolver.maxCoarseLevels=20
momSolver.verbosity=0

#contSolver = fvmbaseExt.AMG()
pc = fvmbaseExt.AMG()
pc.verbosity=1
contSolver = fvmbaseExt.BCGStab()
contSolver.preconditioner = pc
contSolver.relativeTolerance = 1e-1
contSolver.nMaxIterations = 20
contSolver.verbosity=0
contSolver.absoluteTolerance = 1e-25
#contSolver.maxCoarseLevels=20

foptions = fmodel.getOptions()
foptions.transient = True
foptions.setVar('timeStep',timeStep)

foptions.momentumLinearSolver = momSolver
foptions.pressureLinearSolver = contSolver

foptions.momentumTolerance=1e-4
foptions.continuityTolerance=1e-4
foptions.setVar("momentumURF",0.9)
foptions.setVar("pressureURF",0.1)
foptions.printNormalizedResiduals=True

"""
if atype=='tangent':
    vcMap = fmodel.getVCMap()
    for i,vc in vcMap.iteritems():
        print vc.getVar('viscosity')
        vc.setVar('viscosity',(1.7894e-5,1))
"""
#import ddd
fmodel.init()

octree = fvmbaseExt.Octree()

octree.Impl(mesh0, geomFields)



#mpmFileName = fileBase + "MPMs-fullbeam.dat"

#solid = fvmbaseExt.MPM(mpmFileName)

solid = fvmbaseExt.MPM()
#mpm-fvm coupling

mpm_fvm = MPMCoupling( meshes, fmodel, flowFields, geomFields, solid)
print "mpm_fvm done"
option = 1

advanceUnsteady(fmodel,meshes,globalTime,numTimeSteps,  mpm_fvm)

t1 = time.time()

print 'solution time = %f' % (t1-t0)


writer = exporters.FluentDataExporterA(reader,fileBase+"P=83593-fullbeam-test.dat",False,0)
writer.init()
writer.writeScalarField(flowFields.pressure,1)
writer.writeVectorField(flowFields.velocity,111)
writer.writeScalarField(flowFields.massFlux,18)
writer.finish()

if (atype=='tangent'):
    writer = exporters.FluentDataExporterA(reader,fileBase+"-prism-tangent.dat",False,1)
    writer.init()
    writer.writeScalarField(flowFields.pressure,1)
    writer.writeVectorField(flowFields.velocity,111)
    writer.writeScalarField(flowFields.massFlux,18)
    writer.finish()

vFile.close()
pFile.close()
#mFile.close()
