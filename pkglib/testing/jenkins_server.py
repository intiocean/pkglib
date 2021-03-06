'''
Created on 25 Apr 2012

@author: eeaston
'''
import os.path
import shutil

import jenkins

from pkglib import CONFIG

from server import HTTPTestServer


class JenkinsTestServer(HTTPTestServer):
    port_seed = 65533

    def __init__(self, **kwargs):
        super(JenkinsTestServer, self).__init__(**kwargs)
        self.api = jenkins.Jenkins(self.uri)

    @property
    def run_cmd(self):
        if not CONFIG.jenkins_war:
            raise ValueError("jenkins_war missing from org config")

        return [CONFIG.java_executable,
                '-Dcom.sun.akuma.Daemon=daemonized',
                '-Xmx1G',
                '-DJENKINS_HOME=%s' % self.workspace,
                '-jar', CONFIG.jenkins_war,
                '--logfile=%s/jenkins.log' % self.workspace,
                '--httpPort=%s' % self.port,
                '--httpListenAddress=%s' % self.hostname,
                '--ajp13Port=-1',
                '--httpsPort=-1',
                '--debug=5',
                '--handlerCountMax=10',
                '--handlerCountMaxIdle=2',
                ]

    def load_plugins(self, plugins_repo, plugins=None):
        """plugins_repo is the place from which the plugins can be copied to this jenskins instance
           is plugins is None, all plugins will be copied, else is should be a list of the plugin names
        """

        if not os.path.isdir(plugins_repo):
            raise ValueError('Plugin repository "%s" does not exist' % plugins_repo)

        # copy the plugins to the jenkins plugin directory
        available_plugins = dict(((os.path.splitext(os.path.basename(x))[0], os.path.join(plugins_repo, x))
                       for x in os.listdir(plugins_repo) if x.endswith('.hpi')))

        if plugins is None:
            plugins = available_plugins.keys()
        else:
            if isinstance(plugins, basestring):
                plugins = [plugins]

            errors = []
            for p in plugins:
                if p not in available_plugins:
                    if p not in errors:
                        errors.append(p)
            if errors:
                if len(errors) == 1:
                    e = 'Plugin "%s" is not present in the repository' % errors[0]
                else:
                    e = 'Plugins %s are not present in the repository' % sorted(errors)
                raise ValueError(e)

        for p in plugins:
            tgt = os.path.join(self.plugins_dir, '%s.hpi' % p)
            shutil.copy(available_plugins[p], tgt)

    @property
    def plugins_dir(self):
        return os.path.normpath(os.path.join(self.workspace, 'plugins'))
