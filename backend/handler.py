#coding = utf-8

from tornado import web
import config
from rogas import queryConsole
from rogas import configManager
from rogas.resultManager import QueryResult
import json

class BaseHandler(web.RequestHandler):
    """ base of handlers
    """
    def _processRequest(self, func): 
        actResult = dict() 
        tab_index = 0
        try:
            tab_index = self.get_argument('tab_index')
            queryResult = func(self)
            actResult = {'tab_index': tab_index, 'result': queryResult.asReturnResult()}
        except Exception as reason: 
            actResult['tab_index'] = tab_index 
            actResult['result'] = QueryResult('string', str(reason)).asReturnResult()

        self.write(actResult)

class MainHandler(BaseHandler):
    def get(self):
        self.render(config.MAIN_HTML, setting_dict=configManager.getConfigDict())

class QueryHandler(BaseHandler):
    def post(self):
        def _process(self):
            query = self.get_argument('query')
            return queryConsole.start(query)

        self._processRequest(_process)

class LoadResultHandler(BaseHandler):
    def post(self):
        def _process(self):
            query_id = int(self.get_argument('query_id'))
            is_next = int(self.get_argument('is_next'))
            return queryConsole.fetch(query_id, is_next)

        self._processRequest(_process)

class ConfigHandler(BaseHandler):
    def post(self):
        try:
            config_dict_str = self.get_argument('config')
            config_dict = json.loads(config_dict_str)
            configManager.updateConfig(config_dict)
        except Exception as reason: 
            print 'update config error:', reason
        self.write({"state": "done"})

class RelationCoreInfoHandler(BaseHandler):
    def post(self):
        def _process(self):
            return queryConsole.getRelationCoreInfo()

        self._processRequest(_process)

class GraphicalViewInfoHandler(BaseHandler):
    def post(self):
        def _process(self):
            return queryConsole.getGraphicalViewInfo()

        self._processRequest(_process)

class RelationTableInfoHandler(BaseHandler):
    def post(self):
        def _process(self):
            table_name = self.get_argument('table_name')
            return queryConsole.getRelationTableInfo(table_name)

        self._processRequest(_process)

class GraphicalGraphInfoHandler(BaseHandler):
    def post(self):
        def _process(self):
            graph_name = self.get_argument('graph_name')
            return queryConsole.getGraphicalGraphInfo(graph_name)

        self._processRequest(_process)
