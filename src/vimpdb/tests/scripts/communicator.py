import optparse
import sys
parser = optparse.OptionParser()
parser.add_option('--servername', dest="server_name")
parser.add_option('--remote-expr', dest="expr")
parser.add_option('--remote-send', dest="command")


parser.parse_args(sys.argv)

if hasattr(parser.values, 'expr'):
    print parser.values.expr, parser.values.server_name
if hasattr(parser.values, 'command'):
    print parser.values.command, parser.values.server_name
