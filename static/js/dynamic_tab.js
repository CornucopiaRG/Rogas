$(function () {
    //bind ctrl+enter shortcut on the first tab
    $('#query_text0').on('keydown', '', 0, queryTextShortcutKey);

    var tab_index = 1;
    $('#query_add a[role="button"]').on('click', function () { 
        //insert one query at the last of query tabs
        $('ul#query_tab li:last-child').before('<li id="query' + tab_index + '"><a href="#query_content' + tab_index + '" data-toggle="tab"> <strong id="query_tab_name' + tab_index +'"> Query' + tab_index + ' </strong> <button type="button" class="btn btn-warning btn-xs" onclick="removeTab(' + tab_index + ');"><span class="glyphicon glyphicon-remove"></span></button></a></li>');

        //insert one query content(the input panel) into the tab content
        $('div#query_tab_content > div:last-child').after('\
            <div class="tab-pane fade" id="query_content' + tab_index + '">\
                <div class="panel-body">\
                    <form class="form-horizontal" id="query_form' + tab_index + '" method="post" action="/query">\
                        <div class="form-group has-success">\
                            <div class="col-md-11">\
                                <textarea id="query_text' + tab_index + '" class="form-control" rows="1" placeholder="Input query here" onclick=initExpanding(' + tab_index + ')></textarea>\
                            </div>\
                            <div class="col-md-1">\
                                <button id="query_btn' + tab_index + '" type="button" onclick=runQuery(' + tab_index + ') class="btn btn-success">\
                                    <span class="glyphicon glyphicon-expand"></span>\
                                </button>\
                            </div>\
                        </div>\
                    </form>\
                </div>\
            </div>');

        $('#query_text' + tab_index).on('keydown', '', tab_index, queryTextShortcutKey);

        //focus on new tab
        $('ul#query_tab li:eq(-2) a').click();

        tab_index += 1;
    });
});

function queryTextShortcutKey(event)
{
    if (event.ctrlKey && event.keyCode == 13)
    {
        var tab_index = event.data;
        var is_btn_disabled = $('#query_btn' + tab_index).is(':disabled');
        if (!is_btn_disabled)
            $('#query_btn' + tab_index).click();
    }
}

function initExpanding(tab_index)
{
    $('#query_content' + tab_index + ' textarea').expanding();
    $('#query_content' + tab_index + ' textarea').select();
}

function removeTab(tab_index) 
{
    //remove tab from query tabs
    $('ul#query_tab > li#query' + tab_index).fadeOut(300, function () { 
        $(this).remove(); 
    });

    //remove tab content
    $('div#query_tab_content div#query_content' + tab_index).remove();

    //show first tab
    $('#query_tab a:first').tab('show') ;

    return false;
}

function prepareResult(tab_index)
{
    //set up button disabled
    $('#query_btn' + tab_index).prop('disabled', true);

    //remove result panel firstly
    if ($('#rg_result' + tab_index).length > 0) {
        $('#rg_result' + tab_index).remove();
    }

    addLoadingAnimation(tab_index);
}

function addLoadingAnimation(tab_index)
{
    //add loading progress
    if ($('#query_progress' + tab_index).length == 0) {
        $('#query_form' + tab_index).after('\
            <div class="progress" id="query_progress' + tab_index + '">\
              <div class="progress-bar progress-bar-striped active" role="progressbar" style="width: 0%">\
              </div>\
              loading\
            </div>');
    }

    loadingAnimation(tab_index);
}

function runQuery(tab_index) 
{
    prepareResult(tab_index);

    var query_str = $('#query_text' + tab_index).val();
    //modify tab name
    var fromIndex = query_str.toLowerCase().indexOf("from");
    var startIndex = fromIndex + 5;
    if (fromIndex == -1)
        startIndex = 0; 
    var tabName = query_str.slice(startIndex, startIndex+8); 
    tabName += "...";
    $('#query_tab_name' + tab_index).html(tabName);

    var args = {'query': query_str, 'tab_index': tab_index};

    $.ajax({url: '/run_query', data: $.param(args), dataType: 'json', type: 'POST',
        success: querySuccess, error: queryError
    });
}

function loadingAnimation(tab_index)
{
    if ($('#query_progress' + tab_index).length > 0) {
        $('#query_progress' + tab_index + ' .progress-bar').attr('style', 'width: 0%');

        $('#query_progress' + tab_index + ' .progress-bar').animate({
            width: "100%"
        }, 5500, function(){
            loadingAnimation(tab_index);
        });
    }
}

function querySuccess(response)
{
    var tab_index = response.tab_index;
    //remove loading progress
    $('#query_progress' + tab_index).remove();
    //enable run button
    $('#query_btn' + tab_index).prop('disabled', false);

    var result_type = response.result.type;
    var result_content = response.result.content;

    var isHaveGraph = (result_type == "table_graph" || result_type == "graph");
    var isHaveTable = (result_type == "table_graph" || result_type == "table");
    var isOnlyGraph = (result_type == "graph");

    var insert_html = ''
    if (result_type != "string")
    {
        var table_content = result_content.table;

        //relation tab
        insert_html = '\
            <!-- result tab: Relation/Graph -->\
            <div class="panel panel-info" id="rg_result' + tab_index + '">\
                <div class="panel-heading">\
                    <ul id="result_tab" class="nav nav-pills">';

        if (isHaveTable)
        {
            insert_html += '\
                        <li class="active">\
                            <a href="#relation' + tab_index + '" data-toggle="tab">\
                                <span class="glyphicon glyphicon-th"></span> <strong> Relation </strong>\
                            </a>\
                        </li>';
        }

        if (isHaveGraph)
        {
            if (isOnlyGraph)
                insert_html += '\
                            <li class="active">';
            else
                insert_html += '\
                            <li>';

            insert_html += '\
                            <a href="#graph' + tab_index + '" data-toggle="tab">\
                                <span class="glyphicon glyphicon-picture"></span> <strong> Graph </strong>\
                            </a>\
                        </li>';
        }

        insert_html += '\
                    </ul>\
                </div>\
                <div id=result_tab_content" class="tab-content">';

        if (isHaveGraph)
        {
            if (isOnlyGraph)
                insert_html += '\
                    <div class="tab-pane fade in active" id="graph' + tab_index + '">';
            else
                insert_html += '\
                    <div class="tab-pane fade" id="graph' + tab_index + '">';

            insert_html += '\
                        <div id="graph_graph' + tab_index + '"></div>\
                        <div id="graph_text' + tab_index + '"></div>\
                </div>';
        }

        if (isHaveTable)
        {
            insert_html += '\
                        <div class="tab-pane fade in active" id="relation' + tab_index + '">\
                            <div class="table-responsive" id="div_table' + tab_index + '">\
                                <table class="table table-bordered table-hover table-striped">\
                                    <thead id="table_head' + tab_index + '">\
                                        <tr class="active">';

            var column_list = table_content.column_list;
            for (var col_index = 0; col_index < column_list.length; ++col_index)
                insert_html += '<th>' + column_list[col_index] + '</th>';
            insert_html += '\
                                        </tr>\
                                    </thead>';

            insert_html += generateTableBodyHTML(tab_index, table_content);

            insert_html += '\
                                </table>\
                            </div> <!-- table-->';

            insert_html += generatePagerHTML(tab_index, table_content);

            insert_html += '\
                        </div> <!-- relation tab-->';
        }

        insert_html += '\
                </div> <!-- result content -->\
            </div>';
    }
    else {
        insert_html = '<div id="rg_result' + tab_index + '">\
                           <div class="alert alert-info" role="alert">\
                               <p>' + result_content + '</p>\
                           </div>\
                       </div>';
    }

    $('#query_form' + tab_index).after(insert_html);

    $('#rg_result' + tab_index).hide(0, function(){
        $('#rg_result' + tab_index).fadeIn();
    });

    if (isHaveGraph)
    {
        var graph_content = result_content.graph;
        drawGraph(tab_index, graph_content);
    }
}

function queryError(response)
{
    console.log("ERROR:", response)
    alert("There is something wrong: can't connect to server, " + response);

    $('button').prop('disabled', false);
}

function loadingNewPage(tab_index, query_id, is_next) 
{
    //set up button disabled
    $('#query_btn' + tab_index).prop('disabled', true);

    var args = {'query_id': query_id, 'tab_index': tab_index, 'is_next': is_next};

    $.ajax({url: '/load_result', data: $.param(args), dataType: 'json', type: 'POST',
        success: queryNewPageSuccess, error: queryError
    });
}

function generateTableBodyHTML(tab_index, table_content)
{
    var row_content = table_content.row_content;
    var table_body_html = '<tbody id="table_body' + tab_index + '">';
    for (var row_index = 0; row_index < row_content.length; ++row_index)
    {
        if (row_index % 2 == 0)
            table_body_html += '<tr>';
        else
            table_body_html += '<tr class="info">';
        for (var col_index = 0; col_index < row_content[row_index].length; ++col_index)
            table_body_html += '<td>' + row_content[row_index][col_index] + '</td>';
        table_body_html += '<tr>';
    }

    table_body_html += '</tbody>';
    return table_body_html;
}

function generatePagerHTML(tab_index, table_content)
{
    pager_html = '';
    var is_begin = table_content.is_begin;
    var is_end = table_content.is_end;
    if (is_end == 0 || is_begin == 0)
    {
        pager_html += '\
                    <nav id="pager' + tab_index + '">\
                        <ul class="pager">'
            
        var query_id = table_content.query_id;
        if (is_begin == 0)
            pager_html += '\
                             <li class="previous"><a role="button" onclick="loadingNewPage(' + tab_index + ', ' + query_id + ', 0); return false" ><span>&larr;</span> Previous </a></li>';
        if (is_end == 0)
            pager_html += '\
                             <li class="next"><a role="button" onclick="loadingNewPage(' + tab_index + ', ' + query_id + ', 1); return false" > Next <span>&rarr;</span></a></li>';
        pager_html += '\
                        </ul>\
                    </nav>';
    }
    return pager_html;
}

function queryNewPageSuccess(response)
{
    var tab_index = response.tab_index;
    //enable run button
    $('#query_btn' + tab_index).prop('disabled', false);

    $('#table_body' + tab_index).remove();
    $('#pager' + tab_index).remove();

    var result_type = response.result.type;
    if (result_type != "table")
        alert("There is something wrong: invalid result type");

    var result_content = response.result.content;
    var table_content = result_content.table;

    var table_body_html = generateTableBodyHTML(tab_index, table_content);
    var pager_html = generatePagerHTML(tab_index, table_content);

    $('#table_head' + tab_index).after(table_body_html);
    $('#div_table' + tab_index).after(pager_html);

    $('#table_body' + tab_index).hide(0, function(){
        $('#table_body' + tab_index).fadeIn();
    });
}
