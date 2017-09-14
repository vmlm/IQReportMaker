from html import escape
import sys

def _row2tr(row, attr=None):
    cols = escape(row).split(',')
    return ('<TR>'
            + ''.join('<TD>%s</TD>' % data for data in cols)
            + '</TR>')
 
def csv2html(txt):
    htmltxt = '<TABLE summary="csv2html program output">\n'
    for rownum, row in enumerate(txt.split('\n')):
        htmlrow = _row2tr(row)
        htmlrow = '  <TBODY>%s</TBODY>\n' % htmlrow
        htmltxt += htmlrow
    htmltxt += '</TABLE>\n'
    return htmltxt

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Use: csvtohtml.py source dest")
    else:
        csvtxt = open(sys.argv[1], "r").read()
        htmltxt = csv2html(csvtxt)
        htmldest = open(sys.argv[2], "w")
        htmldest.write(htmltxt)
        htmldest.close()