
function GetQueryString(name){
    var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if(r!=null)return  unescape(r[2]); return null;
}


function set_optionselected(option_id) {

    var option_name=GetQueryString(option_id)

    //alert(option_name)

    if(option_name !=null && option_name.toString().length>1){

        option=option_name.split("+").join(" ")

        selected_option=document.getElementById(option)

        //alert(selected_option.title)

        if(selected_option!=null){

            if (selected_option.title=="option") {

                selected_option.selected="True"
            }
            else {

                selected_option.style.color="blue"

            }
        }


    }
}



function checkload() { 

    set_optionselected("selected_hash")
    set_optionselected("author_name")
    set_optionselected("branch_name") 
    set_optionselected("selected_file") 
    set_optionselected("selected_sheet") 

}


function setvalue(form_id,select_id) {

    selectobj=document.getElementById(select_id)

    selected=selectobj.selectedIndex

    value=selectobj.options[selected].value

    var value_id=form_id+select_id

    valueobj=document.getElementById(value_id)

    valueobj.value=value

    //alert(valueobj.value)

}


function setpara(form_id){

    setvalue(form_id,"branch_name")

    setvalue(form_id,"author_name")

    setvalue(form_id,"selected_hash")

}

       

