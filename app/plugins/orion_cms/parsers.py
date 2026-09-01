""" Parsers """

CONST_PLAIN_MARKDOWN = 1911117

from sqlalchemy import literal, select, union_all

from sqlalchemy.sql.expression import Select as sqla_select

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import text

from jinja2 import Template

from space_station_stc.forbidden_scripts.forbidden_sql import *
from space_station_stc.orion_manuscript.abc_stc_script import ABC_STC_Script, UnknownCommandError

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

MERMAID_STR = """\n
```mermaid \n
pie title Pie chart 
{% for i in dataset %}
    "{{i.1}}" : {{i.0}} 
{% endfor %} 
```\n

"""


class Orion_ManuScript(ABC_STC_Script):
    """Orion manuscript class wrapper."""

    builded_select : sqla_select
    sql_executed : bool
    headers : list
    dataset : list
    res_text : str

    db_session: AsyncSession

    async def execute_sql( self, sql : str ) -> tuple[ list, list ]:
        query = await self.db_session.execute( sql )
        headers = query.keys()
        return headers, query.all()

    def __init__(self, db_session: AsyncSession ):
        self.calls = []  # record calls for assertions
        self.res_text = ""
        self.sql_executed = False
        self.headers = []
        self.dataset = []
        self.db_session = db_session

    async def cmd_sql(self, args):
        validator = SQLValidator(config_validator)
        sql_code = " ".join( args )
        try:
            await validator.validate( sql_code )
            self.builded_select = await build_select( sql_code )
            self.headers, self.dataset = await self.execute_sql( self.builded_select )
            self.sql_executed = True
        except:
            self.res_text = 'Fail to parse and execute SQL'

    async def cmd_show_table(self, args):
        if self.sql_executed:
            table_str = '<table border="2">'
            table_str += '<thead><tr>'

            # table headers
            for header in self.headers:
              table_str += '<th>' + header + '</th>'

            table_str += '</tr></thead><tbody>'
            for row in self.dataset:
                table_str += '<tr>'

                for value in row:
                    table_str += '<td>' + str( value ) + '</td>'
                table_str += '</tr>'

            table_str += '</tbody></table>'
            self.res_text += table_str
        else:
            self.res_text = 'No dataset to show'

    async def cmd_show_graph(self, args):
        if self.sql_executed:
            
            template_str = MERMAID_STR
            template = Template(template_str)

            graph_str = template.render( { 'dataset' : self.dataset } )
            self.res_text += graph_str
        else:
            self.res_text = 'No dataset to show'

# Execute code as Orion manuscript and return text for web page
async def execute_orion_manusctript( code : str, db_session: AsyncSession ) -> str:

    if code == "":
        return ""

    om_script = Orion_ManuScript( db_session )

    try:
        await om_script.interpret(code)
        return om_script.res_text
    except Exception as e:
        return str(e)
