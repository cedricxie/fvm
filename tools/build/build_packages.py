# Build packages
# Martin Hunt <mmh@purdue.edu>

"""
Build package definitions.
"""

import testing, string, time
from build_utils import *
from config import *
from build import Build
from subprocess import Popen, STDOUT, PIPE
from select import select

# superclass for all packages
class BuildPkg(Build):
    # Some packages require building in the source directory.
    # Others require separate build directories.
    # We don't want to build in our subversion sources. So we define
    # 'copy_sources' as follows:
    #     0 - no copy. Build directory is separate from sources.
    #     1 - copy with symlinks
    #     2 - full copy
    # For tarballs, copy_sources of nonzero means source and build directories are not the same.
    copy_sources = 0

    def __init__(self, bld, sdir):
        debug('BuildPkg Init (%s,%s,%s)' % (self, bld, sdir))
        if not hasattr(self, 'name'):
            self.name = string.lower(self.__class__.__name__)
        self.__class__.name = self.name
        self.is_pkg = (sdir.split('/')[0] == 'pkgs')
        self.psdir = self.sdir = os.path.join(bld.topdir, sdir)
        self.bdir = os.path.join(bld.blddir, "build", self.name)
        self.blddir = bld.blddir
        self.logdir = bld.logdir
        self.libdir = bld.libdir
        self.bindir = bld.bindir
        self.incdir = bld.incdir
        self.bld = bld

    def pstatus(self, state, option=''):
        "update build status"
        if state == 0 or state == None:
            cprint('GREEN', 'ok ' + option)
        elif isinstance(state, int):
            cprint('RED', 'failed ' + option)
            print "Check contents of %s\n" % self.logfile
            os.system("tail -40 " + self.logfile)
            raise CompileException
        else:
            cprint('YELLOW', state)

    def copy_srcs(self):
        copytree(self.sdir, self.bdir, self.copy_sources)

    # unpack tarball
    def unpack_srcs(self):
        dst = self.bdir
        src = self.sdir
        suffix = src.split('.')[-1]

        compress = None
        if suffix == 'tgz' or suffix == 'gz':
            compress = 'z'
        elif suffix == 'bz2':
            compress = 'j'
        elif suffix == 'tar':
            compress = ''

        if compress == None:
            # it wasn't a tarball
            self.copy_srcs()
            return

        if self.copy_sources:
            self.sdir = os.path.join(dst, 'SOURCES')
            os.makedirs(self.sdir)
            self.bdir = os.path.join(dst, 'BUILD')
            os.makedirs(self.bdir)
        else:
            self.sdir = self.bdir
            os.makedirs(self.bdir)

        # If tarballs have everything in a directory with the same name as the tarball,
        # strip out that directory name.
        name = os.path.basename(src)[:-len(suffix)]
        if name.endswith('.'):
            name = name[:-1]
        if name.endswith('.tar'):
            name = name[:-4]

        if not os.access(src, os.R_OK):
            raise IOError ("ERROR: unable to read file %s." % src)

        dir = os.popen("/bin/bash -c 'tar -%stf %s 2> /dev/null'" % (compress, src)).readline().split()[0]
        if dir.startswith('%s/' % name):
            strip = '--strip-components 1'
        else:
            strip = ''
        os.system('tar -C %s %s -%sxf %s' % (self.sdir, strip, compress, src))

    def clean(self):
        self.state = 'clean'
        self.logfile = ''
        self._clean()

    def build(self):
        # Configure
        self.state = 'configure'
        self.bld.database[self.name] = 0 # mark this package as not built
        self.logfile = os.path.join(self.logdir, self.name + "-conf.log")
        remove_file(self.logfile)
        # remove any old sources
        os.system("/bin/rm -rf %s" % self.bdir)
        self.build_start_time = time.time()

        if config(self.name, 'Build') == '':
            inst = self.installed()
            if inst:
                # Check to see if this is a python package
                # that is already in our build lib directory.
                path = python_path(self.name)
                if os.path.commonprefix([path,self.libdir]) != self.libdir:
                    print 'Using installed package %s%s%s' %\
                     (colors['BOLD'], self.name, colors['NORMAL'])
                    self.bld.database[self.name] = self.build_start_time
                    self.bld.database[self.name + '-status'] = 'installed'
                    return

        # get new sources
        self.unpack_srcs()
        os.chdir(self.bdir)
        run_commands(self.name, 'before')

        pmess("CONF", self.name, self.bdir)
        self.pstatus(self._configure())
        # Build
        self.state = 'build'
        self.logfile = os.path.join(self.logdir, self.name + "-build.log")
        remove_file(self.logfile)
        pmess("BUILD", self.name, self.bdir)
        os.chdir(self.bdir)
        self.pstatus(self._build())

        # Install
        self.state = 'install'
        self.logfile = os.path.join(self.logdir, self.name + "-install.log")
        remove_file(self.logfile)
        pmess("INSTALL", self.name, self.blddir)
        os.chdir(self.bdir)
        self.pstatus(self._install())
        self.bld.database[self.name] = self.build_start_time
        self.bld.database[self.name + '-status'] = self.status()
        debug('database[%s] = %s' % (self.name, self.build_start_time))
        debug('database[%s] = %s' % (self.name + '-status', self.bld.database[self.name + '-status']))
        run_commands(self.name, 'after')

    def test(self, tst):
        self.state = 'testing'
        self.logfile = os.path.join(self.logdir, 'testing', self.name)
        pmess("TEST", self.name, self.blddir)
        ok, errs = self._test(tst)
        if errs:
            cprint('YELLOW', "%s OK, %s FAIL" % (ok, errs))
        else:
            cprint('GREEN', "%s OK" % ok)
        return ok, errs

    def sys_log(self, cmd, show=False):
        "Execute a system call and log the result."
        # get configuration variable
        e = config(self.name, self.state)
        e = e.replace('BUILDDIR', self.blddir)
        e = e.replace('SRCDIR', self.sdir)
        e = e.replace('TMPBDIR', self.bdir)
        e = e.replace('LOGDIR', self.logdir)
        cmd = cmd + " " + e
        debug(cmd)
        f = None
        if self.logfile != '':
            f = open(self.logfile, 'a')
            print >> f, "EXECUTING:", cmd
        p = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE)
        pid = p.pid
        plist = [p.stdout, p.stderr]
        done = 0
        while not done:
            rr, wr, er = select(plist, [], plist)
            if er: print 'er=',er
            for fd in rr:
                data = os.read(fd.fileno(), 1024)
                if data == '':
                    plist.remove(fd)
                    if plist == []:
                        done = 1
                else:
                    if fd == p.stderr:
                        print >>f, data,
                        if show: cprint('DYELLOW', data, False)
                    else:
                        if show: print data,
                        print >>f, data,
        if f: f.close()
        try:
            return os.waitpid(pid, 0)[1]
        except:
            return 0

    def add_required(self, deps):
        ''' This method allows packages to conditionally add to the required list. '''
        return deps

    def status(self):
        return 'normal'

    def installed(self):
        return self._installed()

    # subclasses must redefine these
    def _configure(self):
        pass
    def _clean(self):
        pass
    def _build(self):
        pass
    def _install(self):
        pass
    def _installed(self):
        return False
    def _test(self, tst):
        return testing.do_tests(tst, self.name, self.sdir, self.logfile)

