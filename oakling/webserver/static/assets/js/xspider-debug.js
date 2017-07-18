/**
 * Created by mingming on 17-3-8.
 */


jQuery(document).ready(function($)
{
    /* Global Settings */

    // Progress Bar
    var opts = {
        "closeButton": true,
        "debug": false,
        "positionClass": "toast-top-right",
        "onclick": null,
        "showDuration": "500",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    var status_editor = CodeMirror.fromTextArea($(".json")[0], { //script_once_code为你的textarea的ID号
        lineNumbers: true,
        mode: "application/json",　
        lineWrapping: true,
        indentUnit: 4,
        styleActiveLine: true
        });

    var python_editor = CodeMirror.fromTextArea($(".python")[0], { //script_once_code为你的textarea的ID号
        lineNumbers: true,
        mode: "python",　
        indentUnit: 4,
        lineWrapping: true
        });


    /* debug page */


    var ws;
    var flag=false;
    var content=$("#list");
    var prograss_bar=$("#task-prograss .progress-bar");
    var prograss_text=$("#task-prograss .progress-text");
    var run=$("#send");

    function onLoad() {

        var url= "ws://localhost:8080/ws";

        if(location.hostname != "127.0.0.1" &&  location.hostname != "localhost"){
            var url= "ws://" + location.hostname + ":8084/ws";
        }

        ws = new WebSocket(url);

        ws.onopen = function() {
            flag = false;
            toastr.success("Signal Connected.", "Message:", opts);
        };
        ws.onerror = function() {
            flag = true;
            toastr.error("Signal Disconnected.", "Message:", opts);
        };
        ws.onmessage = function (e) {

            console.log(e);
            console.log(e.data);

            var prograss = JSON.parse(e.data).data.prograss;
            var status = JSON.parse(e.data).data.status;
            if(prograss != undefined){
                console.log(prograss);
                prograss_bar.width(prograss+"%");
                prograss_text.html(prograss+"%");
            }
            else if(status != undefined){
                var p_msg = $("<p class=\"text-success\"></br> "+e.data+"</p>") ;
                p_msg.appendTo(content);
            }
            else{
                console.log(status);
                var data = JSON.parse(e.data).data;
                var p_msg = $("<p class=\"text-info\">"+data+"</p>") ;
                p_msg.appendTo(content);
            }
        };
    }


    function sendMsg() {
        var run_command = {};
        run_command["command"] = true;
        run_command["name"] = project_name;
        run_command["signal"] = "run";

        // ws.send(document.getElementById('msg').value);
        ws.send(JSON.stringify(run_command));
    }

    $("#send").click(function() {
        prograss_bar.width("0%");
        prograss_text.html("0%");
        if(flag==true){
            onLoad();
        }
        content.html('<a href="#" class="xe-user-name"> <strong>Debug logging</strong> </a>'+
                     ' <p> <br />logging here...</p>');
        sendMsg();
        });

    onLoad();

    
    //Edit Project
    function editProject(data) {
        $.ajax({
        url: "/api/v1/command/edit",
        method: 'POST',
        dataType: 'json',
        data: data,
        success: function(resp) {
            show_loading_bar({
                delay: .5,
                pct: 100,
                finish: function () {
                    // Redirect after successful login page (when progress bar reaches 100%)
                    if (resp.status == true) {
                        toastr.success(resp.message, "Message:", opts);
                        //setTimeout(function(){ window.location.reload();},600);
                    }
                    else {
                        // alert(resp.reason);
                        toastr.error(resp.message, "Message:", opts);
                    }
                }
            });
        },
        error: function(resp) {
                        show_loading_bar({
                            delay: .5,
                            pct: 100,
                            finish: function () {
                                toastr.error("Network error.", "Message:", opts);
                            }
                        });
                    }
        });

    }
    
    //Save Scripts
    $(".save-script").click(function () {

        var name = $("#script").attr("project");
        var script = python_editor.getDoc().getValue();
        var data = {
            command: true,
            project: name,
            script:script
        };
        // console.log(script);
        editProject(data);

    });
    //Save Scripts Args
    $("#save-parameters").click(function () {

        var name = $("#script").attr("project");
        var parameters = $("#debug-parameters").val();
        var data = {
            command: true,
            project: name,
            args:parameters
        };
        // console.log(script);
        editProject(data);

    });

    // //Run Scripts
    // $(".run-script").click(function () {
    //
    //     var name = $("#script").attr("project");
    //     var data = {
    //         command: true,
    //         project: name
    //     };
    //      console.log(data);
    //      runProject(data);
    // });

    //Run Scripts


    //Run Processor


});



