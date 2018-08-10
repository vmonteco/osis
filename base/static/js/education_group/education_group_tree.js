function switchTreeVisibility() {
    var newTreeVisibility = (sessionStorage.getItem('treeVisibility') === '0') ? '1' : '0';
    sessionStorage.setItem('treeVisibility', newTreeVisibility);
    showOrHideTree()
}

function showOrHideTree() {
    if (sessionStorage.getItem('treeVisibility') === "0") {
        modifyPanelAttribute("none", "col-md-0", "col-md-12");
    } else {
        modifyPanelAttribute("block", "col-md-3", "col-md-9");
    }
}


function modifyPanelAttribute(collapse_style_display, panel_collapse_class, panel_data_class){
    document.getElementById('collapse').style.display = collapse_style_display;
    document.getElementById('panel-collapse').className = panel_collapse_class;
    document.getElementById('panel-data').className = panel_data_class;
}


$(document).ready(function () {
    var $documentTree = $('#panel_file_tree');
    $documentTree.bind("loaded.jstree", function (event, data) {
        data.instance.open_all();
    });
    $documentTree.bind("changed.jstree", function (event, data) {
        document.location.href = data.node.a_attr.href;
    });

    function get_data_from_tree(data) {
        var inst = $.jstree.reference(data.reference),
            obj = inst.get_node(data.reference);
        var args = obj.li_attr.id.split('_');
        var group_element_year_id = args[1];
        var education_group_year_id = args[2];
        return {group_element_year_id: group_element_year_id, education_group_year_id: education_group_year_id};
    }

    function build_url_data(education_group_year_id, group_element_year_id, action) {
        var data = {
            'root_id': root_id,
            'education_group_year_id': education_group_year_id,
            'group_element_year_id': group_element_year_id,
            'action': action,
            'source': url_resolver_match
        };
        return jQuery.param(data);
    }

    var proxy_management_url = "/educationgroups/proxy_management/";

    $documentTree.jstree({
        "core" : {
           "check_callback" : true
        },
        "plugins" : [ "contextmenu" ],
        "contextmenu" : {
            "select_node": false,
            "items" : {
              "select" : {
                  "label" : gettext("Select"),
                  "action" : function (data) {
                    var __ret = get_data_from_tree(data);
                    var education_group_year_id = __ret.education_group_year_id;
                    $.ajax({
                        url: '../select/',
                        dataType: 'json',
                        data: {'child_to_cache_id' : education_group_year_id},
                        type: 'POST',
                        success: function(jsonResponse) {
                            displayInfoMessage(jsonResponse, 'message_info_container')
                        }
                    });
                  },
                  "icon": "fa fa-check-square"
              },

              "move" : {
                 "label" : gettext("Move"),
                 "action" : function (data) {
                     var __ret = get_data_from_tree(data);
                     var group_element_year_id = __ret.group_element_year_id;
                     var education_group_year_id = __ret.education_group_year_id;
                     if (group_element_year_id === '0') {
                        return;
                    }

                    var detach_data = build_url_data(education_group_year_id, group_element_year_id, 'detach');

                    $('#form-modal-content').load(proxy_management_url, detach_data, function () {
                        $('#form-modal').modal('toggle');
                        formAjaxSubmit('#form-modal-body form', '#form-modal');
                    });

                    $.ajax({
                        url: '../select/',
                        data: {'child_to_cache_id' : education_group_year_id},
                        type: 'POST',
                        dataType: 'json',
                    });

                  },
                  "icon": "fa fa-arrow-circle-o-right",
                  "_disabled": function(data) {
                      var __ret = get_data_from_tree(data);
                      var group_element_year_id = __ret.group_element_year_id;
                      return (group_element_year_id === '0');
                  }
              },

              "detach" : {
                 "label" : gettext("Detach"),
                 "action" : function (data) {
                    var __ret = get_data_from_tree(data);
                    var group_element_year_id = __ret.group_element_year_id;
                    var education_group_year_id = __ret.education_group_year_id;
                    if (group_element_year_id === '0') {
                        return;
                    }

                    var detach_data = build_url_data(education_group_year_id, group_element_year_id, 'detach');

                    $('#form-modal-content').load(proxy_management_url, detach_data, function () {
                        $('#form-modal').modal('toggle');
                        formAjaxSubmit('#form-modal-body form', '#form-modal');
                    });
                  },
                  "icon": "fa fa-cut",
                  "_disabled": function(data) {
                      var __ret = get_data_from_tree(data);
                      var group_element_year_id = __ret.group_element_year_id;
                      return (group_element_year_id === '0');
                  }
              },

              "attach" : {
                 "label" : gettext("Attach"),
                 "separator_before": true,
                 "action" : function (data) {
                    var __ret = get_data_from_tree(data);
                    var group_element_year_id = __ret.group_element_year_id;
                    var education_group_year_id = __ret.education_group_year_id;
                    if (group_element_year_id === '0') {
                        return;
                    }

                    var attach_data = build_url_data(education_group_year_id, group_element_year_id, 'attach');

                    window.location.href = proxy_management_url + "?" + attach_data;
                  },
                  "icon": "fa fa-paperclip"
              },
            }
        }
    });

    $("#tree_open_all").click(function(){
        $documentTree.jstree("open_all");

    });

    $("#tree_close_all").click(function(){
        $documentTree.jstree("close_all");

    });

    showOrHideTree();

});