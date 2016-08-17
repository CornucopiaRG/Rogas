'''
The resultManager is to manage the query results

@author: Yan Xiao
'''

from configManager import SingleConfigManager 
import config
import queryConsole
import os
import random
import helper
import pathExecutor
import networkx as nx

class TableResult(object):
    def __init__(self, column_list=None, row_content=None, is_begin=1, is_end=1, total_num=0, query_id=0):
        self.column_list = column_list
        self.row_content = row_content 
        self.is_end = is_end
        self.is_begin = is_begin
        self.query_id = query_id
        self.total_num = total_num 

    def setQueryId(self, query_id):
        self.query_id = query_id

    def asDict(self):
        return {'column_list': self.column_list, 'row_content': self.row_content,
                'is_begin': self.is_begin, 'is_end': self.is_end, 
                'query_id': self.query_id}
    
    def asReturnResult(self):
        return {'table': self.asDict()}

class GraphResult(object):
    def __init__(self, graph_operator, graph_type, graph_name, graph_op_result_name, graph_condition):
        self.setGraphOperator(graph_operator)
        self.setGraphType(graph_type)
        self.setGraphName(graph_name)
        self.setGraphOpResultName(graph_op_result_name)
        self.setGraphCondition(graph_condition)

    def setGraphType(self, graph_type):
        if graph_type not in ['digraph', 'ungraph']:
            raise TypeError('graph type must be digraph or ungraph') 
        self.graph_type = graph_type

    def setGraphOperator(self, graph_operator):
        if graph_operator not in ['all', 'rank', 'cluster', 'path']:
            raise TypeError('graph operator must be all, rank, cluster or path') 
        self.graph_operator = graph_operator
    
    def setGraphName(self, graph_name):
        self.graph_name = graph_name

    def setGraphOpResultName(self, graph_op_result_name):
        self.graph_op_result_name = graph_op_result_name 
    
    def setGraphCondition(self, graph_condition):
        self.graph_condition = graph_condition 

    def _generateRankSelectNodes(self, row_content):
        node_size_dict = {}
        min_value = 1.0
        max_value = 0.0

        #VertexId, Value
        for row in row_content:
            node_value = float(row[1].strip())
            node_size_dict[str(row[0].strip())] = node_value

            if node_value < min_value: 
                min_value = node_value
            if node_value > max_value:
                max_value = node_value

            if len(node_size_dict) > SingleConfigManager.RANK_NODE_MAX_NUM:
                break

        #scale node value for visualizaiion 
        for node_id, node_value in node_size_dict.iteritems():
            node_value = SingleConfigManager.NODE_MIN_SIZE + int((node_value - min_value) * (SingleConfigManager.NODE_MAX_SIZE - SingleConfigManager.NODE_MIN_SIZE) / (0.001 + max_value - min_value))
            node_size_dict[node_id] = node_value
        
        return node_size_dict

    def _createGraphFromEdges(self, graph_edges, graph_type):
        if graph_type == "digraph":
            Graph = nx.DiGraph()
        elif graph_type == "ungraph":
            Graph = nx.Graph()
            
        edge_list = []
        for edge in graph_edges:
            format_edge = int(edge['source']), int(edge['target'])
            edge_list.append(format_edge)
            
        Graph.add_edges_from(edge_list)
        return Graph

    def  _generateRankGraphNodes(self, row_content):
        self.graph_nodes = []

        rank_nodes = self._generateRankSelectNodes(row_content)

        around_nodes = set()
        for edge in self.graph_edges:
            start_node = edge['source']
            end_node = edge['target']
            if start_node in rank_nodes and end_node in rank_nodes:
                continue
            elif start_node in rank_nodes:
                around_nodes.add(end_node)
            elif end_node in rank_nodes:
                around_nodes.add(start_node)

        #find shortest path between two rank nodes
        graph = self._createGraphFromEdges(self.graph_edges, self.graph_type) 
        
        format_edges_set = set()
        for start_node in rank_nodes:
            for end_node in rank_nodes:
                if start_node == end_node:
                    continue

                format_edge = self._formatPathEdge(start_node, end_node)
                if format_edge in format_edges_set: 
                    continue

                format_edges_set.add(format_edge)
                nodes_list = pathExecutor.nodesInShortestPath(graph, int(format_edge[0]), int(format_edge[1]))
                for node_id in nodes_list:
                    node_id = str(node_id)
                    if node_id not in rank_nodes:
                        around_nodes.add(node_id)

        #add selected nodes 
        for node_id in rank_nodes:
            node = {'id': node_id, 'size': rank_nodes[node_id], 'color': 0, 'highlight': 1, 
                    'opacity': 1.0, 'entity_info': self.node_entity_info[node_id]}
            self.graph_nodes.append(node) 
                
        #add nodes around 
        for node_id in around_nodes:
            node = {'id': node_id, 'size': SingleConfigManager.NODE_DEFAULT_SIZE, 'color': 0, 
                    'highlight': 0, 'opacity': 1.0, 'entity_info': self.node_entity_info[node_id]}
            self.graph_nodes.append(node) 
        
    def _generateHighlightClusters(self, row_content): 
        highlight_clusters = set()
        for row in row_content:
            cluster_id = str(row[0].strip())
            highlight_clusters.add(cluster_id)
        return highlight_clusters

    def _generateClusterGraphNodes(self, row_content, highlight_clusters, keep_nodes):
        self.graph_nodes = []
        cluster_id2size = dict()
        cluster_id2nodes = dict()
        cluster_id2edges = dict()
        cluster_id2keep_nodes = dict()
        node_id2cluster_id = dict()
        node_id2score = dict()
        node_id_cluster_id2score_reatio = dict()
        all_nodes_num = 0

        #ClusterId, Size, Members
        for row in row_content:
            cluster_id = str(row[0].strip())
            cluster_size = float(row[1].strip())
            cluster_members = str(row[2].strip())
            node_ids = [node_id.strip() for node_id in cluster_members[1:-1].split(',')]
            all_nodes_num += cluster_size
            
            cluster_id2size[cluster_id] = cluster_size
            cluster_id2nodes[cluster_id] = node_ids
            cluster_id2keep_nodes[cluster_id] = {} 

            for node_id in node_ids:
                node_id2cluster_id[node_id] = cluster_id 
                node_id2score[node_id] = 0
                if node_id not in node_id_cluster_id2score_reatio:
                    node_id_cluster_id2score_reatio[node_id] = dict()

        for node_id in node_id_cluster_id2score_reatio:
            for cluster_id in cluster_id2size:
                node_id_cluster_id2score_reatio[node_id][cluster_id] = 2.0
        
        for node_id, node_value in keep_nodes.iteritems():
            if node_id in node_id2cluster_id:
                cluster_id = node_id2cluster_id[node_id]
                cluster_id2keep_nodes[cluster_id][node_id] = node_value

        need_scale_size = all_nodes_num > SingleConfigManager.CLUSTER_NODE_MAX_NUM

        if need_scale_size:
            total_graph = self._createGraphFromEdges(self.graph_edges, self.graph_type)

        for edge in self.graph_edges:
            start_node = edge['source']
            end_node = edge['target']
            #two node in the same cluster
            source_cluster_id = node_id2cluster_id[start_node]
            target_cluster_id = node_id2cluster_id[end_node]

            if source_cluster_id not in highlight_clusters or target_cluster_id not in highlight_clusters:
                edge['opacity'] = SingleConfigManager.UNHIGHLIGHT_OPACITY

            #score each node if needed
            #1) different score between inner-cluster edge and cluster-cluster edge
            if source_cluster_id == target_cluster_id:
                if need_scale_size:
                    node_id2score[start_node] += 1.0
                    node_id2score[end_node] += 1.0
                    if source_cluster_id not in cluster_id2edges:
                        cluster_id2edges[source_cluster_id] = [] 
                    cluster_id2edges[source_cluster_id].append(edge)
            else:
                edge['length'] = 700 + random.random() * 100
                if need_scale_size:
                    node_id2score[start_node] += node_id_cluster_id2score_reatio[start_node][target_cluster_id]
                    node_id_cluster_id2score_reatio[start_node][target_cluster_id] *= 0.8

                    node_id2score[end_node] += node_id_cluster_id2score_reatio[end_node][source_cluster_id]
                    node_id_cluster_id2score_reatio[end_node][source_cluster_id] *= 0.8

            #2) consider target node's degree
            if need_scale_size:
                node_id2score[start_node] += 0.2 * total_graph.degree(int(end_node))
                node_id2score[end_node] += 0.2 * total_graph.degree(int(start_node))

        if need_scale_size:
            #calculate the size of each cluster
            for cluster_id, cluster_size in cluster_id2size.items():
                cluster_id2size[cluster_id] = max(cluster_size * SingleConfigManager.CLUSTER_NODE_MAX_NUM * 1.0 / all_nodes_num, 5)

            #keep high score nodes
            for cluster_id, cluster_nodes in cluster_id2nodes.iteritems():
                #get nodes num
                max_nodes_num = int(min(len(cluster_nodes), cluster_id2size[cluster_id]))

                #1) keep nodes first
                cluster_nodes_count = 0
                for node_id, node_value in cluster_id2keep_nodes[cluster_id].iteritems():
                    node_opacity = SingleConfigManager.UNHIGHLIGHT_OPACITY if cluster_id not in highlight_clusters else 1.0
                    node = {'id': node_id, 'size': node_value, 'color': cluster_id, 'highlight': 1,
                            'opacity': node_opacity, 'entity_info': self.node_entity_info[node_id]}
                    self.graph_nodes.append(node)
                    cluster_nodes_count += 1

                added_node_id_set = set(cluster_id2keep_nodes[cluster_id])

                score_node_id_pair_lst = [(node_id2score[node_id], node_id) for node_id in cluster_nodes]
                #sort node by score
                sorted_score_node_id_pair_lst = sorted(score_node_id_pair_lst)

                merged_score_nodes_lst = sorted_score_node_id_pair_lst
                #find max component   
                #use ungraph to find connected components if cluster is not single node
                if cluster_id in cluster_id2edges:
                    cluster_graph = self._createGraphFromEdges(cluster_id2edges[cluster_id], "ungraph")
                    components = nx.connected_components(cluster_graph)
                    max_component_nodes = sorted(components, key=lambda x: len(x), reverse=True)[0]
                    max_component_nodes = [str(node_id).strip() for node_id in max_component_nodes]
                    #get component_node, score pair
                    max_component_score_node_pair_lst = [(node_id2score[node_id], node_id) for node_id in max_component_nodes]
                    sorted_component_score_node_pair_lst = sorted(max_component_score_node_pair_lst)

                    #2) max component nodes second, but at most ratio nodes picked from max component
                    picked_max_component_num = int((max_nodes_num - cluster_nodes_count) * SingleConfigManager.CLUSTER_COMPONENT_RATIO)
                    picked_max_component_score_node_lst = sorted_component_score_node_pair_lst[:picked_max_component_num] 
                    picked_max_component_nodes = [score_node[1] for score_node in picked_max_component_score_node_lst]

                    #3) pick neighbors of max component nodes
                    picked_max_component_neighbor_nodes = set()
                    for node_id in picked_max_component_nodes:
                        node_neighbors_lst = cluster_graph.neighbors(int(node_id)) 
                        picked_max_component_neighbor_nodes.update(node_neighbors_lst)
                    picked_max_component_neighbor_score_node_lst = [(node_id2score[str(node_id)], str(node_id)) for node_id in picked_max_component_neighbor_nodes]

                    merged_score_nodes_lst = picked_max_component_score_node_lst + picked_max_component_neighbor_score_node_lst + sorted_score_node_id_pair_lst
                for i in range(len(merged_score_nodes_lst)):
                    if cluster_nodes_count > max_nodes_num:
                        break

                    node_id = merged_score_nodes_lst[i][1]
                    if node_id not in added_node_id_set:
                        node_opacity = SingleConfigManager.UNHIGHLIGHT_OPACITY if cluster_id not in highlight_clusters else 1.0
                        node = {'id': node_id, 'size': SingleConfigManager.NODE_DEFAULT_SIZE, 'color': cluster_id, 
                                'highlight': 0, 'opacity': node_opacity, 'entity_info': self.node_entity_info[node_id]}
                        self.graph_nodes.append(node)
                        added_node_id_set.add(node_id)
                        cluster_nodes_count += 1

        else:
            #keep all nodes 
            for cluster_id, cluster_nodes in cluster_id2nodes.iteritems():
                for node_id in cluster_nodes:
                    node_opacity = SingleConfigManager.UNHIGHLIGHT_OPACITY if cluster_id not in highlight_clusters else 1.0
                    node = {'id': node_id, 'size': SingleConfigManager.NODE_DEFAULT_SIZE, 'color': cluster_id, 
                            'highlight': 0, 'opacity': node_opacity, 'entity_info': self.node_entity_info[node_id]}
                    if node_id in keep_nodes:
                        node['size'] = keep_nodes[node_id]
                    self.graph_nodes.append(node)

    def _formatPathEdge(self, node_one, node_two):
        if self.graph_type == "digraph":
            return (node_one, node_two)

        if node_one < node_two:
            return (node_one, node_two)
        return (node_two, node_one)

    def _generatePathGraphNodes(self, row_content):
        self.graph_nodes = []

        path_nodes_set = set()
        path_edges2path_ids = dict()
        start_end_nodes_set = set()

        #find nodes in the path
        for index, row in enumerate(row_content):
            if index >= SingleConfigManager.PATH_MAX_NUM:
                break

            #PathId, Length, Paths 
            path_id = int(row[0].strip())
            path_nodes = str(row[2].strip())
            path_node_ids = [node_id.strip() for node_id in path_nodes[1:-1].split(',')]

            #get start node and end node for highlight
            if len(path_node_ids) > 0:
                start_end_nodes_set.add(path_node_ids[0])
                start_end_nodes_set.add(path_node_ids[-1])

            for node_id_index, node_id in enumerate(path_node_ids):
                if node_id_index > 0:
                    one_path_edge = self._formatPathEdge(path_node_ids[node_id_index-1], node_id)
                    if one_path_edge not in path_edges2path_ids:
                        path_edges2path_ids[one_path_edge] = set()
                    path_edges2path_ids[one_path_edge].add(path_id)
                
                path_nodes_set.add(node_id)

        #find nodes around the path
        around_path_nodes_set = set()
        for edge in self.graph_edges:
            edge['opacity'] = SingleConfigManager.UNHIGHLIGHT_OPACITY 
            start_node = edge['source']
            end_node = edge['target']
            if start_node in path_nodes_set and end_node in path_nodes_set:
                format_edge = self._formatPathEdge(start_node, end_node) 
                if format_edge in path_edges2path_ids:
                    edge['color'] = min(path_edges2path_ids[format_edge])
                    edge['length'] = 400 + random.random()*100
                    edge['opacity'] = 1.0
            elif start_node in path_nodes_set:
                around_path_nodes_set.add(end_node)
            elif end_node in path_nodes_set:
                around_path_nodes_set.add(start_node)

        #add nodes on the path
        for node_id in path_nodes_set:
            highlight = 1 if node_id in start_end_nodes_set else 0
            node = {'id': node_id, 'size': SingleConfigManager.NODE_DEFAULT_SIZE, 'color': 0, 
                    'highlight': highlight, 'opacity': 1.0, 'entity_info': self.node_entity_info[node_id]}
            self.graph_nodes.append(node) 
                
        #add nodes around the path
        for node_id in around_path_nodes_set:
            node = {'id': node_id, 'size': SingleConfigManager.NODE_DEFAULT_SIZE, 'color': 0, 
                    'highlight': 0, 'opacity': SingleConfigManager.UNHIGHLIGHT_OPACITY, 'entity_info': self.node_entity_info[node_id]}
            self.graph_nodes.append(node) 

    def _generateGraphEdges(self, matGraphFile): 
        self.graph_edges = []
        graph_edges_dict = dict()

        with open(matGraphFile) as f:
            for line in f:
                edge_nodes = line.strip().split()
                format_edge = self._formatPathEdge(str(edge_nodes[0].strip()), str(edge_nodes[1].strip()))
                if format_edge not in graph_edges_dict:
                    graph_edges_dict[format_edge] = 0
                graph_edges_dict[format_edge] += 1

        edge_weights = graph_edges_dict.values()
        edge_max_weight = max(edge_weights) + 1.0 
        edge_min_weight = min(edge_weights) 
        for format_edge, weight in graph_edges_dict.iteritems():
            width = SingleConfigManager.EDGE_MIN_WIDTH + ((weight- edge_min_weight) * (SingleConfigManager.EDGE_MAX_WIDTH - SingleConfigManager.EDGE_MIN_WIDTH) / (edge_max_weight- edge_min_weight))
            edge = {'source': format_edge[0], 'target': format_edge[1],
                    'length': 100 + random.random() * 50, 'width': width, 'color': 0, 'opacity': 1.0}
            self.graph_edges.append(edge)

    def _filterEdgesByNodes(self):
        all_nodes_id_set = set([node['id'] for node in self.graph_nodes])
        new_graph_edges = []

        for edge in self.graph_edges:
            if edge['source'] in all_nodes_id_set and edge['target'] in all_nodes_id_set:
                new_graph_edges.append(edge)

        self.graph_edges = new_graph_edges

    def _generateEntityInfo(self):
        entity_result, id_field = queryConsole.readEntityTableInfo(self.graph_name)
        node_id_index = 0
        for index, column in enumerate(entity_result.column_list):
            if str(column).strip().lower() == str(id_field).strip().lower():
                node_id_index = index
                break

        self.node_columns = entity_result.column_list
        self.node_entity_info = dict()
        
        for node_info in entity_result.row_content: 
            node_id = str(node_info[node_id_index]).strip()
            self.node_entity_info[node_id] = node_info 

    def generateGraph(self):
        #read graph edges from file
        graph_file = helper.getGraph(self.graph_name)
        self._generateGraphEdges(graph_file)

        #read graph nodes entity information
        self._generateEntityInfo()

        #read graph nodes 
        query_result = queryConsole.readTable(self.graph_op_result_name, self.graph_condition)
        if self.graph_operator == 'rank':
            self._generateRankGraphNodes(query_result.row_content)
        elif self.graph_operator == 'path':
            self._generatePathGraphNodes(query_result.row_content)
        elif self.graph_operator == 'cluster':
                highlight_clusters = self._generateHighlightClusters(query_result.row_content)
                #In fact, we only need readTable once if we can parse the condition: limit xx order by xx
                cluster_result = queryConsole.readTable(self.graph_op_result_name, "")
                self._generateClusterGraphNodes(cluster_result.row_content, highlight_clusters, dict())
        else:
            highlight_clusters = self._generateHighlightClusters(query_result.row_content)
            self._generateClusterGraphNodes(query_result.row_content, highlight_clusters, dict())

        #filter edges by nodes
        self._filterEdgesByNodes()

    def asDict(self):
        return {'name': self.graph_name, 'operator': self.graph_operator, 
                'graph_type': self.graph_type, 'nodes': self.graph_nodes,
                'edges': self.graph_edges, 'entity_columns': self.node_columns,
                'display_node_id': SingleConfigManager.DISPLAY_NODE_ID
                }
    
    def asReturnResult(self):
        return {'graph': self.asDict()}

class TableGraphResult(object):
    def __init__(self, table_result, graph_result):
        self.table_result = table_result
        self.graph_result = graph_result
    
    def asReturnResult(self):
        return {'table': self.table_result.asDict(), 'graph': self.graph_result.asDict()}

class QueryResult(object):
    def __init__(self, result_type='string', result_content='None'):
        #type: string, table, table+graph
        self.setType(result_type)
        self.setContent(result_content)

    def setType(self, result_type):
        if result_type not in ['string', 'table', 'graph', 'table_graph']:
            raise TypeError('Query result type must be string, table , graph or table_graph') 
        self.result_type = result_type
    
    def setContent(self, result_content):
        self.result_content = result_content
    
    def asReturnResult(self):
        content_val = self.result_content if self.result_type == 'string' else self.result_content.asReturnResult()
        return {'type': self.result_type, 'content': content_val}

class ResultManager(object):
    def __init__(self):
        self.current_id = 0
        self.cursor_dict = {}

    def _extractTableResult(self, cursor, is_next, max_number, is_all=False):
        start_index = cursor.rownumber 
        #previous page
        if is_next == 0:
            #if current in last page
            if cursor.rownumber == cursor.rowcount:
                start_index = cursor.rownumber - max_number - cursor.rowcount % max_number 
            else:
                start_index = cursor.rownumber - 2*max_number
        start_index = 0 if start_index < 0 else start_index

        if start_index >= cursor.rowcount:
            return 1, TableResult([], [])

        column_list = [desc[0] for desc in cursor.description]
        rows_content = []

        cursor.scroll(start_index, mode='absolute')
        rows = cursor.fetchall() if is_all else cursor.fetchmany(max_number)
        for each_row in rows:
            one_row_content = [str(each_col) for each_col in each_row]
            rows_content.append(one_row_content)

        is_end = 1 if cursor.rownumber == cursor.rowcount else 0
        is_begin = 1 if start_index == 0 else 0

        return is_end, TableResult(column_list, rows_content, is_begin, is_end, cursor.rowcount)

    def extractTableResultFromCursor(self, cursor, is_all=False):
        is_end, table_result = self._extractTableResult(cursor, 0, config.PAGE_MAX_NUM, is_all)
        
        if is_end == 0:
            table_result.setQueryId(self.current_id)
            self.addCursor(cursor) 
        
        return table_result

    def addCursor(self, cursor):
        self.cursor_dict[self.current_id] = cursor
        self.current_id += 1
    
    def removeCursor(self, id):
        self.cursor_dict.pop(id)

    def extractTableResultById(self, id, is_next):
        if id not in self.cursor_dict:
            return TableResult([], [])

        cursor = self.cursor_dict[id]
        _, table_result = self._extractTableResult(cursor, is_next, config.PAGE_MAX_NUM)
        table_result.setQueryId(id)

        return table_result

SingleResultManager = ResultManager()
