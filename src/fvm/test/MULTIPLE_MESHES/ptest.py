#!/usr/bin/env python

"""
Given script and destination directory,
this run the script in the destinationdirectory and compared
results in destination directory/GOLDEN and return 0 in success

Usage: ptest.py [options]
Options:
  --outdir       Directory where test data is written. Default is current dir.
  --np           Number of processors. Default is 1.
  --in           Input file (required).
  --golden       Directory where golden results are kept.
  --script       Script to run (required).
"""

import sys, os
from optparse import OptionParser
import numfile_compare

def usage():
    print __doc__
    sys.exit(-1)

def cleanup(ec):
    sys.exit(ec)

def check_mesh(options):
    for np in range(0,options.np):
       check_file = os.path.join(options.outdir, 'mesh_PROC%s.dat' % np)
       reference_file = os.path.join(options.golden, 'mesh_PROC%s.dat' % np)
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "mesh files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "mesh files are ok"
    return 0


def check_cell_site(options):
    for np in range(0,options.np):
       check_file = os.path.join(options.outdir, 'MESHDISMANTLER_cellSite_proc%s.dat' % np)
       reference_file = os.path.join(options.golden, 'MESHDISMANTLER_cellSite_proc%s.dat' % np)
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "cell site files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "cell site files are ok"
    return 0


    
def check_face_site(options):
    for np in range(0,options.np):
       check_file = os.path.join(options.outdir, 'MESHDISMANTLER_faceSite_proc%s.dat' % np)
       reference_file = os.path.join(options.golden, 'MESHDISMANTLER_faceSite_proc%s.dat' % np)
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "face site files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "face site files are ok"
    return 0

def check_node_site(options):
    for np in range(0,options.np):
       check_file = os.path.join(options.outdir, 'MESHDISMANTLER_nodeSite_proc%s.dat' % np)
       reference_file = os.path.join(options.golden, 'MESHDISMANTLER_nodeSite_proc%s.dat' % np)
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "node site files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "node site files are ok"
    return 0

def check_cells_mapper(options):
    for np in range(0,options.np):
       check_file = os.path.join(options.outdir, 'MESHDISMANTLER_cellsMapper_proc%s.dat' % np)
       reference_file = os.path.join(options.golden, 'MESHDISMANTLER_cellsMapper_proc%s.dat' % np)
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "cells mapper files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "cells mapper files are ok"
    return 0

def check_face_cells(options):
    for np in range(0,options.np):
       check_file = os.path.join(options.outdir, 'MESHDISMANTLER_faceCells_proc%s.dat' % np)
       reference_file = os.path.join(options.golden, 'MESHDISMANTLER_faceCells_proc%s.dat' % np)
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "face cells files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "face cells files are ok"
    return 0


def check_nodes_mapper(options):
    for np in range(0,options.np):
       check_file = os.path.join(options.outdir, 'MESHDISMANTLER_nodesMapper_proc%s.dat' % np)
       reference_file = os.path.join(options.golden, 'MESHDISMANTLER_nodesMapper_proc%s.dat' % np)
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "nodes mapper files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "nodes mapper files are ok"
    return 0

def check_face_nodes(options):
    for np in range(0,options.np):
       check_file = os.path.join(options.outdir, 'MESHDISMANTLER_faceNodes_proc%s.dat' % np)
       reference_file = os.path.join(options.golden, 'MESHDISMANTLER_faceNodes_proc%s.dat' % np)
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "face nodes files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "face nodes files are ok"
    return 0

def check_scatter_mappers(options):
    for np in range(0,options.np):
       check_file = os.path.join(options.outdir, 'MESHDISMANTLER_scatterMappers_proc%s.dat' % np)
       reference_file = os.path.join(options.golden, 'MESHDISMANTLER_scatterMappers_proc%s.dat' % np)
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "scatter mappers files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "scatter mappers files are ok"
    return 0

def check_gather_mappers(options):
    for np in range(0,options.np):
       check_file = os.path.join(options.outdir, 'MESHDISMANTLER_gatherMappers_proc%s.dat' % np)
       reference_file = os.path.join(options.golden, 'MESHDISMANTLER_gatherMappers_proc%s.dat' % np)
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "gather mappers files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "gather mappers files are ok"
    return 0

def assembler_check_face_cells(options):
    for np in range(0,options.np):
       check_file     = os.path.join(options.outdir, 'MESHASSEMBLER_faceCells.dat')
       reference_file = os.path.join(options.golden, 'MESHASSEMBLER_faceCells.dat')
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "face cells files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "face cells files are ok"
    return 0

def assembler_check_globalCellToMeshID(options):
    for np in range(0,options.np):
       check_file     = os.path.join(options.outdir, 'MESHASSEMBLER_globalCellToMeshID.dat')
       reference_file = os.path.join(options.golden, 'MESHASSEMBLER_globalCellToMeshID.dat')
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "global cell to meshid files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "global cell to meshid files are ok"
    return 0


def assembler_check_localNodeToGlobal(options):
    for np in range(0,options.np):
       check_file     = os.path.join(options.outdir, 'MESHASSEMBLER_localNodeToGlobal.dat')
       reference_file = os.path.join(options.golden, 'MESHASSEMBLER_localNodeToGlobal.dat')
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "local node to global files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "local node to global files are ok"
    return 0

def assembler_check_localToGlobal(options):
    for np in range(0,options.np):
       check_file     = os.path.join(options.outdir, 'MESHASSEMBLER_localToGlobal.dat')
       reference_file = os.path.join(options.golden, 'MESHASSEMBLER_localToGlobal.dat')
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "local to global files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "local to global files are ok"
    return 0

def assembler_check_sites(options):
    for np in range(0,options.np):
       check_file     = os.path.join(options.outdir, 'MESHASSEMBLER_sites.dat')
       reference_file = os.path.join(options.golden, 'MESHASSEMBLER_sites.dat')
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "site files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "site files are ok"
    return 0

def assembler_check_syncLocalToGlobal(options):
    for np in range(0,options.np):
       check_file     = os.path.join(options.outdir, 'MESHASSEMBLER_syncLocalToGlobal.dat')
       reference_file = os.path.join(options.golden, 'MESHASSEMBLER_syncLocalToGlobal.dat')
       if numfile_compare.check_files(check_file, reference_file, 1.0e-5):
         print "syncLocalToGlobal files didn't match GOLDEN/* !!!!!!!!!!!!!"
         return  -1
         break;
    print "syncLocalToGlobal files are ok"
    return 0


def check_convergence(options):
    check_file     = os.path.join(options.outdir, 'convergence.dat')
    reference_file = os.path.join(options.golden, 'convergence.dat')
    if numfile_compare.check_files(check_file, reference_file, 1.0e-8):
       print "convergence history files didn't match GOLDEN/* !!!!!!!!!!!!!"
       return  -1
      # break;
    print "convergence history files are ok"
    return 0
    


def main():
    funcs = {
        'testThermalParallelJacobi.py':[check_convergence],
        'testMultiMeshesDismantlerCellSite.py'      :[check_cell_site],
        'testMultiMeshesDismantlerFaceSite.py'      :[check_face_site],
        'testMultiMeshesDismantlerNodeSite.py'      :[check_node_site],
        'testMultiMeshesDismantlerCellsMapper.py'   :[check_cells_mapper],
        'testMultiMeshesDismantlerFaceCells.py'     :[check_face_cells],
        'testMultiMeshesDismantlerNodesMapper.py'   :[check_nodes_mapper],
        'testMultiMeshesDismantlerFaceNodes.py'     :[check_face_nodes],
        'testMultiMeshesDismantlerScatterMappers.py':[check_scatter_mappers],
        'testMultiMeshesDismantlerGatherMappers.py' :[check_gather_mappers],
        'testMeshAssemblerFaceCells.py'             :[assembler_check_face_cells],
        'testMeshAssemblerGlobalCellToMeshID.py'    :[assembler_check_globalCellToMeshID],
        'testMeshAssemblerLocalNodeToGlobal.py'     :[assembler_check_localNodeToGlobal],
        'testMeshAssemblerLocalToGlobal.py'         :[assembler_check_localToGlobal],
        'testMeshAssemblerSites.py'                 :[assembler_check_sites],
        'testMeshAssemblerSyncLocalToGlobal.py'     :[assembler_check_syncLocalToGlobal]
    }
    parser = OptionParser()
    parser.set_defaults(np=1,outdir='',type='tri')
    parser.add_option("--in", dest='infile', help="Input file (required).")
    parser.add_option("--golden", help="Directory where golden files are stored.")
    parser.add_option("--np", type=int, help="Number of Processors.")
    parser.add_option("--outdir", help="Output directory.")
    parser.add_option("--script", help="Script to run.")
    parser.add_option("--type", help="'tri'[default], 'quad', 'hexa', or 'tetra'")
    parser.add_option("--xdmf", action='store_true', help="Dump data in xdmf")
    (options, args) = parser.parse_args()

    # convert path to absolute because we may cd to the test directory
    options.script   = os.path.abspath(options.script)
    options.outdir   = os.path.abspath(options.outdir)
    options.golden   = os.path.abspath(os.path.join(options.golden,'GOLDEN'))
    options.infile   = os.path.abspath(options.infile)

    if options.outdir:
        if not os.path.isdir(options.outdir):
            try:
                os.makedirs(options.outdir)
            except:
                print "error creating directory " + options.outdir
                sys.exit(1)
        os.chdir(options.outdir)

    mpi = 'mpirun -np %s %s %s --type=%s' % (options.np, options.script, options.infile, options.type);
    if options.xdmf:
        mpi += ' --xdmf'

    if os.system( mpi ):
        cleanup(-1)

    for f in funcs[os.path.basename(options.script)]:
        err = f(options)
        if err:
            cleanup(err)

if __name__ == "__main__":
    main()

