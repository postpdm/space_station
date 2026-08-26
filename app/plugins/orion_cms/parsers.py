""" Parsers """

CONST_PLAIN_MARKDOWN = 1911117

async def execute_orion_manusctript( code : str ) -> str:
    some_data = ''
    
    
    res = ''
    print( code )
    for line in code.splitlines():
        if line.lower() == 'show table':
            res += '<table border="2"><tbody><tr><td>' + some_data + '</td></tr></tbody></table>'
        else:
            if (line.lower() ).startswith('select'):
                some_data = line
            else:
                res = 'Unknown command ' + line
        
    return res