function updateConfig()
{
    var cluster_node_max_num = Number($('#cluster_node_max_num').val());
    var cluster_component_ratio = Number($('#cluster_component_ratio').val());
    var ranked_node_max_num = Number($('#ranked_node_max_num').val());
    var path_max_num = Number($('#path_max_num').val());
    var node_min_size = Number($('#node_min_size').val());
    var node_max_size = Number($('#node_max_size').val());
    var node_default_size = Number($('#node_default_size').val());
    var edge_min_width = Number($('#edge_min_width').val());
    var edge_max_width = Number($('#edge_max_width').val());
    var unhighlight_opacity = Number($('#unhighlight_opacity').val());
    var dispaly_node_id = $('#dispaly_node_id').is(':checked');
    var do_visualization = $('#do_visualization').is(':checked');

    if (cluster_node_max_num < 0 || cluster_component_ratio < 0 || ranked_node_max_num < 0 || path_max_num < 0 || node_min_size < 0 || node_max_size < 0 
        || node_default_size < 0 || edge_min_width < 0 || edge_max_width < 0 || unhighlight_opacity < 0)
    {
        alert("Parameters can't be negative");
        return;
    }

    if (unhighlight_opacity > 1.0)
    {
        alert("UnhighlightOpacity can't be larger than 1.0");
        return;
    }

    if (cluster_component_ratio > 1.0)
    {
        alert("ClusterComponentRatio can't be larger than 1.0");
        return;
    }

    if (node_min_size >= node_max_size)
    {
        alert("NodeMinSize must be smaller than NodeMaxSize");
        return;
    }

    if (edge_min_width >= edge_max_width)
    {
        alert("EdgeMinWidth must be smaller than EdgeMaxWidth");
        return;
    }

    var config_obj= {'CLUSTER_NODE_MAX_NUM': cluster_node_max_num,
                     'CLUSTER_COMPONENT_RATIO': cluster_component_ratio,
                     'RANK_NODE_MAX_NUM': ranked_node_max_num,
                     'PATH_MAX_NUM': path_max_num,
                     'NODE_MIN_SIZE': node_min_size,
                     'NODE_MAX_SIZE': node_max_size,
                     'NODE_DEFAULT_SIZE': node_default_size,
                     'EDGE_MIN_WIDTH': edge_min_width,
                     'EDGE_MAX_WIDTH': edge_max_width,
                     'UNHIGHLIGHT_OPACITY': unhighlight_opacity,
                     'DISPLAY_NODE_ID': dispaly_node_id,
                     'DO_VISUALIZATION': do_visualization 
                    };
    var config_str = JSON.stringify(config_obj);
    var args = {'config': config_str};

    $.ajax({url: '/update_config', data: $.param(args), dataType: 'json', type: 'POST',
        success: configSuccess, error: configError 
    });
}

function configSuccess(response)
{
    alert("Update setting successfully");
}

function configError(response)
{
    alert("Can't connect to the backend server");
}
