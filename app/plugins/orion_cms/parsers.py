""" Parsers """

CONST_PLAIN_MARKDOWN = 1911117

from sqlalchemy import literal, select, union_all

from sqlalchemy.sql.expression import Select as sqla_select

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import text

from forbidden_scripts.forbidden_sql import *

config_validator = SQLValidatorConfig(
    allowed_tables={"cms_page", },
    allowed_fields={"id", "title", "created_at"},
    allow_star=False,
    allowed_functions={"DATE","COUNT", "SUM", "MAX", "MIN"},
    forbidden_functions={"SLEEP", "BENCHMARK"},
    max_subquery_depth=1,
    allow_cte=True,
)

async def build_select( sql : str ) -> sqla_select:
    return text( sql )

async def execute_orion_manusctript( code : str, db_session: AsyncSession ) -> str:
    prepared_select = None
    executed = False
    query = None
    dataset = None

    res = ''
    for line in code.splitlines():
        if line.lower() == 'show table':
            try:
                res = '<table border="2">'
                if not executed:
                    query = await db_session.execute( prepared_select )
                    dataset = query.all()
                    res += '<thead><tr>'

                    # table headers
                    headers = query.keys()
                    for header in headers:
                      res += '<th>' + header + '</th>'

                    executed = True
                res += '</tr></thead><tbody>'
                for row in dataset:
                    res += '<tr>'
                    row_dict = row._mapping
                    for value in row:   
                        res += '<td>' + str( value ) + '</td>'
                    res += '</tr>'

                res += '</tbody></table>'
            except Exception as e:
                res = 'Error in SQL execution ' + e
        else:
            if (line.lower() ).startswith('select'):
                try:
                    # validate SQL string
                    validator = SQLValidator(config_validator)
                    validator.validate( line )
                    prepared_select = await build_select( line )
                except Exception as e:
                    res = 'Error in SQL parsing ' + e
            else:
                res = 'Unknown command ' + line

    return res