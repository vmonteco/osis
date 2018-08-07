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
                    var inst = $.jstree.reference(data.reference),
                        obj = inst.get_node(data.reference);
                    var education_group_year_id = obj.li_attr.id.split('_').slice(-1)[0]
                    $.ajax({
                        url: '../select/',
                        data: {'child_to_cache_id' : education_group_year_id},
                        type: 'POST',
                        dataType: 'json',
                    });
                  },
                  "icon": "fa fa-check-square"
              },

              "move" : {
                 "label" : gettext("Move"),
                 "action" : function (data) {
                    var inst = $.jstree.reference(data.reference),
                        obj = inst.get_node(data.reference);
                    var args = obj.li_attr.id.split('_');
                    var group_element_year = args[1];
                    if (group_element_year === '0') {
                        return;
                    }
                    var education_group_year_id = args[2];
                    /*
                    * TODO : Use tree_management proxy instead of building URLs here
                    * */
                    var detach_url = "/educationgroups/"
                       + root_id
                       + "/"
                       + education_group_year_id
                       + "/content/"
                       + group_element_year
                       + "/management/?action=detach&source="
                       + url_resolver_match;

                    $.ajax({
                        url: '../select/',
                        data: {'child_to_cache_id' : education_group_year_id},
                        type: 'POST',
                        dataType: 'json',
                    });

                    $('#form-modal-content').load(detach_url, function () {
                        $('#form-modal').modal('toggle');
                        formAjaxSubmit('#form-modal-body form', '#form-modal');
                    });
                  },
                  "icon": "fa fa-arrow-circle-o-right",
                  "_disabled": function(data) {
                      var inst = $.jstree.reference(data.reference),
                          obj = inst.get_node(data.reference);
                      var args = obj.li_attr.id.split('_');
                      var group_element_year = args[1];
                      return (group_element_year === '0');
                  }
              },

              "detach" : {
                 "label" : gettext("Detach"),
                 "action" : function (data) {
                    var inst = $.jstree.reference(data.reference),
                        obj = inst.get_node(data.reference);
                    var args = obj.li_attr.id.split('_');
                    var group_element_year = args[1];
                    if (group_element_year === '0') {
                        return;
                    }
                    var education_group_year_id = args[2];

                    var detach_url = "/educationgroups/"
                       + root_id
                       + "/"
                       + education_group_year_id
                       + "/content/"
                       + group_element_year
                       + "/management/?action=detach&source="
                       + url_resolver_match;

                    $('#form-modal-content').load(detach_url, function () {
                        $('#form-modal').modal('toggle');
                        formAjaxSubmit('#form-modal-body form', '#form-modal');
                    });
                  },
                  "icon": "fa fa-cut",
                  "_disabled": function(data) {
                      var inst = $.jstree.reference(data.reference),
                          obj = inst.get_node(data.reference);
                      var args = obj.li_attr.id.split('_');
                      var group_element_year = args[1];
                      return (group_element_year === '0');
                  }
              },

              "attach" : {
                 "label" : gettext("Attach"),
                 "separator_before": true,
                 "action" : function (data) {
                    var inst = $.jstree.reference(data.reference),
                        obj = inst.get_node(data.reference);
                    var args = obj.li_attr.id.split('_');
                    var group_element_year = args[1];
                    var education_group_year_id = args[2];

                    var attach_url = "/educationgroups/"
                        + root_id
                        + "/"
                        + education_group_year_id
                        + "/content/"
                        + group_element_year
                        + "/management/?action=attach";
                    window.location.href = attach_url;
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