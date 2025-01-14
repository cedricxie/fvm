from build_packages import *

class Sympy(BuildPkg):
    requires = ['scipy', 'python']

    def _installed(self):
        return python_package('sympy', [0,7,0])

    def _install(self):
        do_env("LDFLAGS=")
        ret = self.sys_log("python setup.py install --prefix=%s" % self.blddir)
        do_env("LDFLAGS=", unload=True)
        return ret

