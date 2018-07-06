$(function() {
  $.ajaxSetup({error: function(jqXHR){
    $(location).attr('href', '/login/?next=/dashboard/')
  }})
  $.ajaxSetup({
    headers: { "X-CSRFToken": csrf_token }
  });
  block_resizer();
  dragbar();

  getInvList();
  $("#eb > div:nth-child(3) > div > span").off("mousedown").on("mousedown", function() {getInvList();})
  getGroupList();

  //inventory selector
  $("ul:first-of-type").on("click", function() {
    a='';
    getGroupList($(".custom-combobox>input").val());
    $("#hosts, #vars, #groups").html('');
  })
//group selector
  $("ul:nth-of-type(2)").on("click", function() {
    loadGroupDetails(`/inventory/${$(".custom-combobox>input").val()}/groups/${$("#gr>.custom-combobox>input").val()}`);
    $("#delGr").removeClass("w3-disabled");
  });

})

var a = ''; // path to the group "/inventory/<NAME>/groups/<NAME>
var b = ''; // path to the host "/inventory/<NAME>/hosts/<NAME>

function dragbar() {
  var drbar_width = $(window).width()*0.006;
  var sidebar_width = $(window).width()*0.005;
  $("#dragbar").width(drbar_width);
  $("#dragbar2").width(drbar_width);
  $("#dragbar").draggable({
    axis: "x",
    containment: [40, 0, $("#dragbar2").offset().left-drbar_width],
    scroll: false,
    stop: function(){
      $("#col1").css("width", $("#dragbar").offset().left - sidebar_width);
      $("#col2").css("width", $("#dragbar2").offset().left - $("#dragbar").offset().left - sidebar_width );
      $("#col2").offset({left: $("#dragbar").offset().left + sidebar_width});
      $( "#dragbar2" ).draggable({containment : [$("#dragbar").offset().left + drbar_width + 40, 0, $(window).width()-60]})
    }
  });
  $( "#dragbar2" ).draggable({
    axis: "x",
    containment: [$("#dragbar").offset().left + drbar_width + 40, 0, $(window).width()-40],
    scroll: false,
    stop: function(){
      $("#dragbar" ).draggable({
        containment : [20, 0, $("#dragbar2").offset().left - drbar_width]
      });
      $("#col3").css("width", $(window).width() - $("#dragbar2").offset().left - drbar_width - sidebar_width);
      $("#col2").css("width", $("#dragbar2").offset().left-$("#dragbar").offset().left - sidebar_width);
    }
  })
}

function block_resizer() {
  var ratio = $(".w3-bar").height()*100/$(window).height();
  $(".column").css("top", (ratio+1)+"%");
  $(".column").css("height", (100-(ratio+1.5))+"%");
  $(".dragbar").css("top", (ratio+1)+"%");
  $(".dragbar").css("height", (100-(ratio+1.5))+"%");
  if  ($(window).width() > 1200) {
    $("#col3").css("width", $(window).width()*0.99 - $("#dragbar2").offset().left);
    $(".column").css("position", "absolute");
    $(".dragbar").css("visibility", "visible");
    $("#col1").css("margin-top", 0);
  }
  else if ($(window).width() <= 1200) {
    $(".dragbar").css("visibility", "hidden");
    $("#col1").css("margin-top", $(".w3-bar").height());
    $(".column").css("position", "static");
    $(".column").css("width", "99%");
    $(".column").css("margin-left", "0.5%");
  }
}

function mach() { // get machines and show list
  $.ajax({
    url:"/api/machines",
    data: {"json": "render"},
    success:function(data) {
      var html =`<a href="javascript:void(0)" class="right close" onclick='$("#modal").css("display", "none");'>&times;</a>
                 <h2>Machines: <button class="plus" onclick="showForm('mach')">+</button></h2><div id="machform"></div>`;
      $('#modal_content').html(html + data);
      $('#modal').css("display", "block");
    }
  })
}

function getInvList() { // get inventories and prepare selector
  $.ajax({
    url:"/api/inventories",
    success:function(data){
      var html = '<option value="">Select one...</option>';
      var invs = data;
//      $.ajax({
//        url:"/dashboard/limit",
//        complete:function(data) {
//          var limit=data.responseText;
//          if (invs.length >= limit) {$('#addInv').off('click').addClass('w3-disabled')}
//          else {$('#addInv').removeClass('w3-disabled').off('click').on('click', function(){showForm("inventory")})}
//        }
//      })
$('#addInv').removeClass('w3-disabled').off('click').on('click', function(){showForm("inventory")})
      for (n in invs) {html +=`<option value="${invs[n]}">${invs[n]}</option>`;}
      $("#combobox").html(html)
    }
  })
}

function getSelector(items) {
  var selector = '<option value="">Select one...</option>'
  for (n in items) {
    selector +=`<option value="${items[n]}">${items[n]}</option>`;
  }
  return selector;
}

function groupSelectorBuilder(groups, selected_group){

  //  var html ='<div id ="gr" class="ui-widget"><select id="combobox2"></select>\
  //  <button id="delGr" class="w3-disabled">DEL</button><button id="addGr">ADD</button></div>';
  //   $("#sidepanel").html(html);
  if(selected_group == undefined) { // group is not selected
    $("#gr > span > input").val("");
    $("#delGr").off("click").addClass("w3-disabled");
  }
  $("#addGr").removeClass("w3-disabled");
  selector = getSelector(groups);
  $("#combobox2").html(selector);
  $("#combobox2").combobox();
  $("#gr>.custom-combobox>input").val(selected_group);
  $("#gr > span").off("mousedown").on("mousedown", function() { // refresh groups list
    //      getGroupList($(".custom-combobox>input").val());
    if ($(".custom-combobox>input").val() != '') { // inventory is selected
      $.ajax({
        url: "/api/inventory/" + $(".custom-combobox>input").val() + "/groups",
        success:function(data){
          selector = getSelector(data);
          $("#combobox2").html(selector);
          $("#combobox2").combobox();
        }
      })
    }
  })
  block_resizer();
}

function getGroupList(inv) {
  if (a && a!='') {
    var selected_group = a.split("/")[a.split("/").length-1];
  }
  var x = {};
  if (inv) {
    $.ajax({
      url: "/api/inventory/" + inv + "/groups",
      success:function(data){
        groupSelectorBuilder(data, selected_group);
        $("#delInv").removeClass("w3-disabled");
        $("#delInv").off("click").on("click", function(){del("/api/inventory/" + inv)});
        $("#addGr").on("mousedown", function(){ $("#inventoryform").unbind('focusout')});
        $("#addGr").off("click").on("click", function(){showForm('group');});
        $("#addGr").on("mouseup", function(){ $("#inventoryform").html('')});
      }
    })
  } else {
    groupSelectorBuilder();
    $("#delInv").off("click").addClass("w3-disabled");
    $("#addGr").off("click").addClass("w3-disabled");
  }
}

function getGroupHostVars(path) {
  b=path;
  $.ajax({
    url: "/api" + path + "/host_vars",
    success:function(data){
      var html = `
      <a href="javascript:void(0)" class="right close" onclick='$("#modal").css("display", "none"); b="";'>&times;</a>
      <h2>Host vars: <button class="plus" onclick="showForm('hostVar')">+</button></h2><br>
      <div id="hostvarform"></div><br><table>`;

      Object.keys(data).sort().forEach(function(key){
        var value = data[key].replace(/&/g, '&amp;')
        .replace(/>/g, '&gt;')
        .replace(/</g, '&lt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');

        html +=`<tr><td style="width: auto">${key}:</td><td>
        <form action="/api${b}/host_vars/" style="display: inline" onchange="sendForm($(this))">
        <input type="hidden" name = "path" value = "${b}"><input type="hidden" name = "Var" value = "${key}">
        <input type="text" name = "newVal" value="${value}">
        </form></td><td>
        <a class="minus" href="javascript:void(0)" onclick="del('/api'+b+'/host_vars/${key}')">-</a><td>`
      })
      html += '</table>';
      $("#modal_content").html(html);
      $('form').submit(function(event){event.preventDefault();})
      $("#modal").css("display", "block");
    }
  })
}

function loadGroupDetails(group) {
    a = group;
    loadVars(group);
    loadHosts(group);
    loadChildren(group);
  }

function loadHosts(group) {
    $("#delGr").removeClass("w3-disabled");
    $("#delGr").off("click").on("click", function(){del("/api" + a)});
    $.ajax({
      url: "/api" + group + "/hosts",
      success:function(data){
        var html =`<button class="plus" onclick="showForm('host')">+</button><br><div id="hostform"></div><table>`;
        var hosts = data;
        for (n in hosts) {html += `
          <tr><td><a href="javascript:void(0)"
          onclick = "getGroupHostVars('/inventory/${$(".custom-combobox>input").val()}/host/${hosts[n]}')">${hosts[n]}</a>
          </td><td><a class="minus" href="javascript:void(0)" onclick="del('/api${a}/hosts/${hosts[n]}')">-</a></td></tr>`
        }
        html += '</table>';
        $("#hosts").html(html);
      }
    })
}

function loadVars(group) {
  $.ajax({
    url: "/api" + group + "/vars",
    success:function(data){
      var html ='<button class="plus" onclick="showForm(\'var\')">+</button><br><div id="var"></div><table>';
      Object.keys(data).sort().forEach(function(key){
        var value = data[key].replace(/&/g, '&amp;')
        .replace(/>/g, '&gt;')
        .replace(/</g, '&lt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
        html +=`<tr><td>${key}:</td><td><form action="/api${a}/vars/" style="display: inline" onchange="sendForm($(this))">
        <input type="text" name = "newVal" value="${value}"><input type="hidden" name = "group" value = "${a}">
        <input type="hidden" name="Var" value="${key}"></form></td><td><a class="minus" href="javascript:void(0)"
        onclick="del('/api${a}/vars/${key}')">-</a></td></tr>`})
        html += '</table>';
        $("#vars").html(html);
        $('form').submit(function(event){event.preventDefault();})
    }
  })
}

function loadChildren(group) {
  $.ajax({
    url: "/api" + group + "/children",
    success:function(data){
      var children = data;
      var html =`<button class="plus" onclick="showForm('child')">+</button><br><div id="child"></div><table>`;
      var inventory = $(".custom-combobox>input").val();
      for (n in children) {
        html += `
        <tr><td><a href="javascript:void(0)" onclick = "loadGroupDetails('/inventory/${inventory}/groups/${children[n]}');
        $('#gr>.custom-combobox>input').val('${children[n]}');">${children[n]}</a></td>
        <td><a class="minus" href="javascript:void(0)" onclick="del('/api${a}/children/${children[n]}');">-</a></td></tr>`}
        html += '</table>';
        $("#groups").html(html);
      }
    })
  }

    function del(data) {
      $.ajax({
        url: data,
        type: 'DELETE',
        success:function(data){
          switch (data.details) {
            case "inventory":
              a ='';
              $(".custom-combobox>input").val("");
              getGroupList();
              getInvList();
              $("#hosts, #vars, #groups").html('');
              break;
          case "hostvar":
            getGroupHostVars(b);
            break

          case "group":
            a='';
            getGroupList($(".custom-combobox>input").val());
            $("#hosts, #vars, #groups").html('');
            break;

          case "var":
            loadVars(a);
            break;
          case "host":
            loadHosts(a);
            break;
          case "child":
            loadChildren(a);
            break;
          case "machine":
            mach();
            break;
      }
    }
  })
}

function sendForm(form) { // update variable
  $.ajax({
    url: form.attr("action") + form.find('input[name="Var"]').val(),
    type: 'POST',
    contentType: 'multipart/form-data',
    data: form.find('input[name="newVal"]').val(),
  })
}

function simpleForm(form, action, animated) {
  var html = `<form action='${action}'><input type="text" oninput="validateForm(this)"><button type="submit">add</button></form>`;
  form.html(html);
  if (animated) {form.find("form").addClass("w3-animate-left")}
  form.find("input[type='text']").focus();
  form.focusout(function(e) {
    if (!$.contains($(this).context, e.relatedTarget)){
      $(this).html('').unbind('focusout');
    }
  });
}

function variableForm(form, action) {
  var html = `<form action="${action}">
    <input type="text" name="newVar" placeholder="Name" oninput="validateForm(this)"> :
    <input type="text" name = "newVal" placeholder="Value"><nobr>
    <button type="submit");">add</button></form>`;
    form.html(html);
    form.find("input[name='newVar']").focus();
    form.focusout(function(e) {
      if (!$.contains($(this).context, e.relatedTarget)){
        $(this).html('').unbind('focusout');
      }
    });
}

function comboboxForm(form, action, combo_id, endpoint) {
  html = `<form action="${action}">
  <select id="${combo_id}"></select>
  <button type="submit" style="margin-left: 40px;">add</button></form>`
  form.html(html);
  var combobox = form.find('select');
  $.ajax({
    url: endpoint,
    success: function(data){
      selector = getSelector(data);
      combobox.html(selector);
    }
  })
  combobox.combobox();
  // clear error to resend form
  form.find("select + span a.ui-button").on( "click", function() {
    form.find('select + span input.custom-combobox-input')[0].setCustomValidity("");
  });
  form.find("input").focus();
  form.focusout(function(e) {
    if (!$.contains($(this).context, e.relatedTarget)){
      $(this).html('').unbind('focusout');
    }
  });
}

    function showForm(form){

      switch (form) {
        case "inventory":
          var action = '/api/inventory/';
          var form = $("#inventoryform");
          simpleForm(form, action, animated = true);
          block_resizer();
          break;

        case "group":
          var action = `/api/inventory/${$(".custom-combobox>input").val()}/groups/`;
          var form = $("#groupform");
          simpleForm(form, action, animated = true);
          block_resizer();
          break;

        case "var":
          var action = `/api${a}/vars/`;
          var form = $("#var");
          variableForm(form, action);
          break;

        case "host":
          var action = `/api${a}/hosts/`;
          var combo_id = "combobox1";
          var form = $("#hostform");
          var endpoint = "/api/machines";
          comboboxForm(form, action, combo_id, endpoint);
          break;

        case "child":
          var action = `/api${a}/children/`;
          var combo_id = "combobox3";
          // var current_group = $("#gr>.custom-combobox>input").val();
          var form = $("#child");
          var endpoint = "/api/inventory/" + $(".custom-combobox>input").val() + "/groups";
          comboboxForm(form, action, combo_id, endpoint);
          break;

        case "hostVar":
          var action = `/api${b}/host_vars/`;
          var form = $("#hostvarform");
          variableForm(form, action);
          break;

        case "mach":
          var form = $("#machform");
          var action = "/api/machines/";
          simpleForm(form, action);
          break;
        }

        $('form').submit(function(event){
          var form = $(this);
          // hide form if empty
          if (form.find('input[type="text"], select').val() == '') {
            $(this).html('').unbind('focusout');
            return false;
          }
          $.ajax({
            url: form.attr("action") + form.find('input[type="text"], select').val(),
            type: 'PUT',
            data: form.find('input[name="newVal"]').val(),
            success:function(data){
              if (typeof data == 'string'){  // show errors
                form.find('input[type="text"], input.custom-combobox-input')[0].setCustomValidity(data);
                form.find("button").click();
                return;
              }
              switch (data.details) {
                case "var":
                case "host":
                case "child":
                  loadGroupDetails(a); break;
                case "hostvar":
                  getGroupHostVars(b); break;
                case "machine" :
                  mach(); break;
                case "inv":
                  getInvList();
                  $("#inventoryform").html('');
                  break;
                case  "group":
                  getGroupList($(".custom-combobox>input").val());
                  $("#groupform").html(''); break;
              }
            }
          });
          event.preventDefault();
        });
      }

      function validateForm(input) {
        if (input.name == 'newGroup') {
          var re = /^([A-Za-z0-9_:-])+$/;
        } else {
          var re = /^[A-Za-z0-9-_:.-]+$/;
        }
        if (re.test(input.value)) {
          input.setCustomValidity("");
        } else {
          input.setCustomValidity("Используйте символы a-z0-9-_:");
        }
      }

      $(window).resize(function() {block_resizer(); })

      /*
      //search
      function searchGroup() {
      var input, filter, group, row;
      input = $("#myInput").val();
      input = input.toLowerCase();
      row = $(".group");
      group = $(".groupName");
      console.log(group);
      for (i = 0; i<row.length; i++) {
      if (group[i].innerHTML.indexOf(input) > -1) {
      row[i].style.display = "";
    } else {
    row[i].style.display = "none";
  }
}
}
*/
