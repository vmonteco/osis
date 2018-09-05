const proxy_management_url = "/educationgroups/proxy_management/";


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

    $documentTree.bind("state_ready.jstree", function () {
        $documentTree.bind("select_node.jstree", function (event, data) {
            document.location.href = data.node.a_attr.href;
        });
    });

    function get_data_from_tree(data) {
        var inst = $.jstree.reference(data.reference),
            obj = inst.get_node(data.reference);

        return {
            group_element_year_id: obj.a_attr.group_element_year,
            education_group_year_id: obj.a_attr.education_group_year,
            element_type: obj.a_attr.element_type
        };
    }

    function build_url_data(education_group_year_id, group_element_year_id, action, element_type) {
        var data = {
            'root_id': root_id,
            'education_group_year_id': education_group_year_id,
            'group_element_year_id': group_element_year_id,
            'action': action,
            'source': url_resolver_match,
            'element_type': element_type
        };
        return jQuery.param(data);
    }

    $documentTree.jstree({
            "core": {
                "check_callback": true,
                "data": tree,
            },
            "plugins": [
                "contextmenu",
                // Plugin to save the state of the node (collapsed or not)
                "state",
            ],
            "state": {
                // the key is important if you have multiple trees in the same domain
                // The key includes the root_id
                "key": location.pathname.split('/', 3).join('/'),
                "opened":true,
                "selected": false,
            },
            "contextmenu": {
                "select_node": false,
                "items": {
                    "select": {
                        "label": gettext("Select"),
                        "action": function (data) {
                            var __ret = get_data_from_tree(data);
                            var element_id = __ret.education_group_year_id;
                            var element_type = __ret.element_type;
                            $.ajax({
                                url: proxy_management_url,
                                dataType: 'json',
                                data: {'element_id': element_id, 'element_type': element_type, 'action': 'select'},
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
                            var education_group_year_id = __ret.education_group_year_id;
                            var element_type = __ret.element_type;
                            var attach_data = build_url_data(education_group_year_id, group_element_year_id, 'attach',
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
                            var education_group_year_id = __ret.education_group_year_id;
                            var element_type = __ret.element_type;
                            if (group_element_year_id === '0') {
                                return;
                            }

                            var detach_data = build_url_data(education_group_year_id, group_element_year_id, 'detach',
                                element_type);

                            $('#form-modal-content').load(proxy_management_url, detach_data, function () {
                                $('#form-modal').modal('toggle');
                                formAjaxSubmit('#form-modal-body form', '#form-modal');
                            });

                            $.ajax({
                                url: '../select/',
                                data: {'child_to_cache_id': education_group_year_id},
                                type: 'POST',
                                dataType: 'json',
                            });
                        },
                    }
                }
            }
        }, 'open_all'
    );

    showOrHideTree();

});
