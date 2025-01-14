def geometry(g, t, l, w):
    import cubit
    cubit.init('[]')
    print "Other side of initializing"
    cubit.cmd('reset')
    print "resetting"    
    offset = (g + t/2.0)
    cubit.cmd('brick x 700 y 300 z 10')
    cubit.cmd('move volume 1 location 0 0 %e' %(5.e0-offset))
    cubit.cmd('create surface rectangle width 80 height 200 zplane')
    cubit.cmd('create surface rectangle width 80 height 200 zplane ')
    cubit.cmd('create surface rectangle width 80 height 200 zplane')
    cubit.cmd('move surface 7 location 95 0 -%e' % offset)
    cubit.cmd('move surface 8 location -95 0 -%e' % offset)
    cubit.cmd('move surface 9 location 0 0 -%e' % offset)
    
    cubit.cmd('webcut volume 1 with plane normal to curve 16 close_to vertex 12')
    cubit.cmd('webcut volume 1 with plane normal to curve 16 close_to vertex 9')
    cubit.cmd('webcut volume 6 with plane normal to curve 17 close_to vertex 14')
    cubit.cmd('webcut volume 7 with plane normal to curve 69 close_to vertex 13')
    cubit.cmd('webcut volume 8 with plane normal to curve 43 close_to vertex 18')
    cubit.cmd('webcut volume 9 with plane normal to curve 104 close_to vertex 17')
    cubit.cmd('webcut volume 10 with plane normal to curve 118 close_to vertex 10')
    cubit.cmd('webcut volume 11 with plane normal to curve 133 close_to vertex 9')
    cubit.cmd('imprint volume all with volume all')
    cubit.cmd('merge all')

    cubit.cmd('curve all interval 60')
    cubit.cmd('curve 13 15 17 19 21 23 77 78 111 112 141 142 interval 10')
    cubit.cmd('curve 14 16 18 20 22 24 53 54 55 56 58 60 75 92 105 122 137 139 interval 20')
    cubit.cmd('curve 93 94 95 96 125 126 127 128 interval 2')
    cubit.cmd('curve 61 62 63 64 149 150 151 152 interval 30')
    cubit.cmd('curve 37 38 39 40 45 46 47 48 interval 10')
    cubit.cmd('curve 2 4 6 8 interval 94')

    cubit.cmd('mesh curve  37 38 39 40 45 46 47 48 94 96 125 127 13 15 17 19 21 23 77 78 111 112 141 142 14 16 18 20 22 24 53 54 55 56 58 75 92 105 122 139')
    cubit.cmd('surface all scheme SubMap')
    cubit.cmd('mesh surface all')
    cubit.cmd('mesh volume all')
    cubit.cmd('Volume all scale 1.e-6 ')
    cubit.cmd('Sideset 1 surface 7 8 9')
    cubit.cmd('Sideset 2 surface 3 5 16 17 18 19 21 22 23 24 26 29 32 34 41 52 54 63 72 74 81 87 89')
    cubit.cmd('block 1 volume all')
    cubit.cmd('export Fluent "backgroundMesh.msh" Block all Sideset all overwrite')

    cubit.cmd('reset')
    cubit.cmd('create surface rectangle width %e height %e zplane'  % (l,  w))
    cubit.cmd('curve 2 4  interval 20')
    cubit.cmd('curve 1 3  interval 360')
    cubit.cmd('mesh curve all')
    cubit.cmd('mesh surface all')
    cubit.cmd('Sideset 1 curve 2 4 ')
    cubit.cmd('Sideset 2 curve 1 3')
    cubit.cmd('block 1 surface 1')
    #cubit.cmd('volume all scale 1e-6')
    cubit.cmd('export Fluent "beam.msh" Block all Sideset all overwrite')
    cubit.cmd('reset')
    cubit.destroy()
