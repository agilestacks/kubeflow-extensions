from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring, construct_parser)
from IPython.core.magic import (line_magic, cell_magic, line_cell_magic, Magics, magics_class)
from IPython import get_ipython
from IPython.display import display, HTML

import os.path
import pystache

@magics_class
class ArgoMagics(Magics):

    @magic_arguments()
    @argument('filename',
        help="Worfklow file"
    )
    @line_magic
    def argo_workflow(self, line):
        args = parse_argstring(self.template, line)
        filename = args.filename
        return display( HTML(url=filename) )
        