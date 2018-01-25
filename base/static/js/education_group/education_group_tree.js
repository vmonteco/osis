function showDiv() {
    if (document.getElementById('collapse').style.display == "block") {
        document.getElementById('collapse').style.display = "none";
        document.getElementById('panel-collapse').className = "col-md-0";
        document.getElementById('panel-data').className = "col-md-12";
        document.getElementById('link_identification').href = "{% url 'education_group_read' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=0";
        document.getElementById('link_diploma').href = "{% url 'education_group_diplomas' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=0";
        document.getElementById('link_general_information').href = "{% url 'education_group_general_informations' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=0";
        document.getElementById('link_administrative').href = "{% url 'education_group_administrative' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=0";
        document.getElementById('link_content').href = "{% url 'education_group_content' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=0";
    }
    else {
        document.getElementById('collapse').style.display = "block";
        document.getElementById('panel-collapse').className = "col-md-3";
        document.getElementById('panel-data').className = "col-md-9";
        document.getElementById('link_identification').href = "{% url 'education_group_read' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=1";
        document.getElementById('link_diploma').href = "{% url 'education_group_diplomas' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=1";
        document.getElementById('link_general_information').href = "{% url 'education_group_general_informations' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=1";
        document.getElementById('link_administrative').href = "{% url 'education_group_administrative' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=1";
        document.getElementById('link_content').href = "{% url 'education_group_content' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=1";
    }
}

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

$(document).ready(function () {
    var $documentTree = $('#panel_file_tree');
    $documentTree.bind("loaded.jstree", function (event, data) {
        data.instance.open_all();
    });
    $documentTree.bind("changed.jstree", function (event, data) {
        document.location.href = data.node.a_attr.href;
    });
    $documentTree.jstree();


    if (getParameterByName('tree') === "0") {
        document.getElementById('collapse').style.display = "none";
        document.getElementById('panel-collapse').className = "col-md-0";
        document.getElementById('panel-data').className = "col-md-12";
        document.getElementById('link_identification').href = "{% url 'education_group_read' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=0";
        document.getElementById('link_diploma').href = "{% url 'education_group_diplomas' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=0";
        document.getElementById('link_general_information').href = "{% url 'education_group_general_informations' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=0";
        document.getElementById('link_administrative').href = "{% url 'education_group_administrative' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=0";
        document.getElementById('link_content').href = "{% url 'education_group_content' education_group_year_id=education_group_year.id %}?root={{ parent.id}}&tree=0";
    }
});