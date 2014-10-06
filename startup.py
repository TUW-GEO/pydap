"""A file-based Pydap server running on Gunicorn.

Usage:
  pydap [options]

Options:
  -h --help                     Show this help message and exit
  --version                     Show version
  -i --init DIR                 Create directory with templates
  -b ADDRESS --bind ADDRESS     The ip to listen to [default: 127.0.0.1]
  -p PORT --port PORT           The port to connect [default: 8001]
  -d DIR --data DIR             The directory with files [default: .]
  -t DIR --templates DIR        The directory with templates
  --worker-class=CLASS          Gunicorn worker class [default: sync]

"""

import sys
sys.path.insert(1, "/media/sf_H/Development/python/pydap/src/")
sys.path.insert(1, "/media/sf_H/Development/python/pydap.handlers.netcdf/src/")
sys.path.insert(1, "/media/sf_H/Development/python/pydap.responses.wms/")

import os
from pydap.wsgi.app import init, DapServer, StaticMiddleware, PydapApplication
from pydap.lib import __version__

from beaker.middleware import CacheMiddleware

def main():  # pragma: no cover
    """Run server from the command line."""
    import multiprocessing
    from docopt import docopt

    arguments = docopt(__doc__, version = "Pydap %s" % __version__)

    # init templates?
    if arguments["--init"]:
        init(arguments["--init"])
        return

    # create pydap app
    data, templates = arguments["--data"], arguments["--templates"]
    app = DapServer(data, templates)

    # configure app so that is reads static assets from the template directory
    # or from the package
    if templates and os.path.exists(os.path.join(templates, "static")):
        static = os.path.join(templates, "static")
    else:
        static = ("pydap.wsgi", "templates/static")
    app = StaticMiddleware(app, static)

    app = CacheMiddleware(app, type = 'dbm', data_dir = './cache')

    # configure WSGI server
    workers = multiprocessing.cpu_count() * 2 + 1

    options = {
        'bind': '%s:%s' % ('127.0.0.1', '8001'),
        'workers': workers,
        'timeout': 3600,
    }
    PydapApplication(app, options).run()


if __name__ == '__main__':
    main()
