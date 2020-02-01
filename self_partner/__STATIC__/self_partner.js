var self_partner = function(){
    console.log("[self_partner] active");
    var sdiv;
    var the_name;

    var show_create_group = function(){
	var cg = document.querySelector('#sp_create_group');
	cg.style.display = "";
	var input = document.getElementById("__" + the_name + "_0001");
	input.value = "";
	return false;
    }

    var hide = function(){
	var bd = document.querySelector('#' + the_name + "_score_display");
	if(bd){
	    bd.style.display = "none";
	}
    }

    var hide_message = function(){
	var bd = document.querySelector('#' + the_name + "_message");
	if(bd){
	    bd.style.display = "none";
	}
    }

    var show_message = function(){
	var bd = document.querySelector('#' + the_name + "_message");
	if(bd){
	    bd.style.display = "";
	}
    }

    var hide_current_group = function(){
	var bd = document.querySelector('#sp_current_group')
	if(bd){
	    bd.style.display = "none";
	}
    }

    var show_current_group = function(){
	var bd = document.querySelector('#sp_current_group')
	if(bd){
	    bd.style.display = "";
	}
    }

    var do_submit_click = function(){
	show_message();
	hide_current_group();
	document.getElementById(the_name + "_submit").click();
    }

    var remove_from_group = function(){
	// clicked the remove from group button
	var input = document.getElementById("__" + the_name + "_0002");
	input.value = "remove";
	do_submit_click();
    }

    var setup = function(name){
	the_name = name;
	var sdiv = document.querySelector('#' + name);
	console.log("[self_partner] sdiv=", sdiv);
	// sdiv.innerHTML = "hello world";

	var bd = document.querySelector('#' + name + "_buttons");
	if(bd){
	    bd.style.display = "none";
	}
	bd = document.querySelector('#' + name + "_nsubmits_left");
	if(bd){
	    bd.style.display = "none";
	}
	var qd = document.querySelector('#' + name + "_queue_buttons");
	if(qd){
	    qd.style.display = "none";
	}
	document.querySelector("#sp_create_group_link").onclick = show_create_group;
	var rfg = document.querySelector("#sp_remove_from_group");
	if (rfg){
	    rfg.onclick = remove_from_group;
	}

	// trigger input submit on enter
	["_0000", "_0001"].forEach(function(k){
	    var input = document.getElementById("__" + the_name + k);
	    input.addEventListener("keyup", function(event) {
		if (event.keyCode === 13) {
		    event.preventDefault();
		    do_submit_click();
		}
	    });
	});

	hide();
	hide_message();
    }

    var doit = function(x){
	return eval(x);
    }

    return({ setup: setup,
	     doit: doit,
	     hide: hide,
	   });
}

SP = self_partner();
