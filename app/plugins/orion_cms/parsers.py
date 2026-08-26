""" Parsers """

CONST_PLAIN_MARKDOWN = 1911117

async def execute_orion_manusctript( code : str ) -> str:
    res = ''
    print( code )
    for line in code.splitlines():
        if line.lower() == 'show table':
            res += '<table border="2"><tbody><tr><td>Component</td></tr></tbody></table>'
        else:
            res = 'Unknown command ' + line
        
    return res