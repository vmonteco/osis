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


function modifyPanelAttribute(collapse_style_display, panel_collapse_class, panel_data_class) {
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
        var element_id = args[2];
        var element_type = args[3];
        return {
            group_element_year_id: group_element_year_id,
            element_id: element_id,
            element_type: element_type
        };
    }

    function build_url_data(element_id, group_element_year_id, action, element_type) {
        var data = {
            'root_id': root_id,
            'element_id': element_id,
            'group_element_year_id': group_element_year_id,
            'action': action,
            'source': url_resolver_match,
            'element_type': element_type
        };
        return jQuery.param(data);
    }

    var proxy_management_url = "/educationgroups/proxy_management/";

    $documentTree.jstree({
        "core": {
            "check_callback": true
        },
        "plugins": ["contextmenu"],
        "contextmenu": {
            "select_node": false,
            "items": {
                "select": {
                    "label": gettext("Select"),
                    "action": function (data) {
                        var __ret = get_data_from_tree(data);
                        var element_id = __ret.element_id;
                        var element_type = __ret.element_type;
                        if(element_type === "learningunityear")
                        {
                            var url = '../select_lu/'+element_id;
                        }else{
                            var url = '../select/';
                        }
                        $.ajax({
                            url: url,
                            dataType: 'json',
                            data: {'child_to_cache_id': element_id},
                            type: 'POST',
                            success: function (jsonResponse) {
                                displayInfoMessage(jsonResponse, 'message_info_container')
                            }
                        });
                    }
                },

                "attach": {
                    "label": gettext("Attach"),
                    "separator_before": true,
                    "action": function (data) {
                        var __ret = get_data_from_tree(data);
                        var group_element_year_id = __ret.group_element_year_id;
                        var element_id = __ret.element_id;
                        var element_type = __ret.element_type;
                        var attach_data = build_url_data(element_id, group_element_year_id, 'attach',
                            element_type);
                        window.location.href = proxy_management_url + "?" + attach_data;
                    },
                    "_disabled": function (data) {
                        var __ret = get_data_from_tree(data);
                        return __ret.element_type === "learningunityear";
                    }
                },

                "detach": {
                    "label": gettext("Detach"),
                    "action": function (data) {
                        var __ret = get_data_from_tree(data);
                        var group_element_year_id = __ret.group_element_year_id;
                        var element_id = __ret.element_id;
                        var element_type = __ret.element_type;
                        if (group_element_year_id === '0') {
                            return;
                        }

                        var detach_data = build_url_data(element_id, group_element_year_id, 'detach',
                            element_type);

                        $('#form-modal-content').load(proxy_management_url, detach_data, function () {
                            $('#form-modal').modal('toggle');
                            formAjaxSubmit('#form-modal-body form', '#form-modal');
                        });

                        $.ajax({
                            url: '../select/',
                            data: {'child_to_cache_id': element_id},
                            type: 'POST',
                            dataType: 'json',
                        });
                    },
                }
            }
        }
    });

    showOrHideTree();

});