'''
This is the configuration manager

@author Yan Xiao
'''

import os
import json

config_dump_file = 'config.dump'

class ConfigManager(object):
    def __init__(self):
        self.config_dict = dict()
        self.load()

    def defaultInit(self, cluster_node_max_num=800, cluster_component_ratio=0.5, rank_node_max_num=20, path_max_num=20, node_min_size=15, node_max_size=30, node_default_size=10, edge_min_width=2, edge_max_width=10, unhighlight_opacity=0.2, display_node_id=True, do_visualization=True):
        self.config_dict['CLUSTER_NODE_MAX_NUM'] = cluster_node_max_num
        self.config_dict['CLUSTER_COMPONENT_RATIO'] = cluster_component_ratio
        self.config_dict['RANK_NODE_MAX_NUM'] = rank_node_max_num
        self.config_dict['PATH_MAX_NUM'] = path_max_num
        self.config_dict['NODE_MIN_SIZE'] = node_min_size
        self.config_dict['NODE_MAX_SIZE'] = node_max_size
        self.config_dict['NODE_DEFAULT_SIZE'] = node_default_size
        self.config_dict['EDGE_MIN_WIDTH'] = edge_min_width
        self.config_dict['EDGE_MAX_WIDTH'] = edge_max_width
        self.config_dict['UNHIGHLIGHT_OPACITY'] = unhighlight_opacity
        self.config_dict['DISPLAY_NODE_ID'] = display_node_id 
        self.config_dict['DO_VISUALIZATION'] = do_visualization 
        self.initWithDict(self.config_dict, False)
        
    def initWithDict(self, config_dict, is_dump=True):
        for key, value in config_dict.iteritems():
            value = float(value)
            setattr(self, key, value)
            self.config_dict[key] = value

        if is_dump:
            with open(config_dump_file, 'w') as f:
                json.dump(config_dict, f)

            
    
    def load(self):
        #default init because config file may not contain each item
        self.defaultInit()

        if os.path.exists(config_dump_file):
            with open(config_dump_file) as f:
                config_dict = json.load(f)
                self.initWithDict(config_dict, False)

SingleConfigManager = ConfigManager()

def updateConfig(config_dict):
    SingleConfigManager.initWithDict(config_dict)

def getConfigDict():
    return SingleConfigManager.config_dict
