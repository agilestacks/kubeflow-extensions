from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring, construct_parser)
from IPython.core.magic import (line_magic, cell_magic, line_cell_magic, Magics, magics_class)
from IPython import get_ipython
from IPython.display import display, Markdown, FileLink, Code, HTML

import os.path
import pystache

@magics_class
class TemplateMagics(Magics):

    # def __init__(self, shell):
    #     super(TemplateMagics, self).__init__(shell)
    #     self.ctx = dict

    @magic_arguments()
    @argument('filename',
        help="File path to write results"
    )
    @argument('-v', '--verbose',
        default=False,
        help="Print output",
        action='store_true',
    )
    @cell_magic
    def template(self, line, cell=None):
        """create a template from cell content
        """
        args = parse_argstring(self.template, line)
        filename = args.filename
        template = cell.strip()
        result = mustache(template, params(), filename)
        if args.verbose:
            return display( FileLink(filename), Code(result) )
        else:
            return display( FileLink(filename) )


    @magic_arguments()
    @argument('template',
        help="File path to template"
    )
    @argument('-o', '--output',
        default=None,
        help="Filename to write output"
    )
    @argument('-f', '--format',
        default='mustache',
        help="Template format (mustache or fstring)"
    )
    @argument('-v', '--verbose',
        default=False,
        help="Print output",
        action='store_true',
    )
    @line_magic
    def templatefile(self, line):
        """creates a file from template stored as a file
        """
        args = parse_argstring(self.templatefile, line)
        if not os.path.isfile(args.template):
            raise FileNotFoundError(args.template)

        with open( args.template ) as f:
            fread = f.read()

        output = args.output
        p = params()
        if args.format == 'mustache':
            result = mustache(fread, p, output)
        elif args.foramt == 'fstring':
            result = fstring(fread, p, output)
        else:
            raise ValueError(f'Unsupported format: {args.format}. Must be: mustache|fstring')

        if output and args.verbose:
            return display( FileLink(output), Code(result) )
        elif output:
            return display( FileLink(output) )
        else:
            return display( Code(result) )

def fstring(template, params=dict(), filename=None):
    r = template.format(params)
    if filename != None:
        with open(filename, 'w') as f:
            f.write(r)
    return r


def mustache(template, params=dict(), filename=None):
    r = pystache.render(template, params)
    if filename != None:
        with open(filename, 'w') as f:
            f.write(r)
    return r

def params(ns=get_ipython().user_ns):
    envvars = ns.get('environ', {})
    blacklist = ['In', 'Out', 'environ']
    globvars = {k: v for k, v in ns.items() if not k.startswith('_') and k not in blacklist} 
    return {**envvars, **globvars}

