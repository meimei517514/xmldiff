
function GetQueryString(name){
    var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if(r!=null)return  unescape(r[2]); return null;
}


function set_optionselected(option_id) {

    var option_name=GetQueryString(option_id);

    if(option_name !=null && option_name.toString().length>1){

        option=option_name.split("+").join(" ")

        selected_option=document.getElementById(option)

        //alert(option_id)

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


function set_filechosen() {

    var file_name=GetQueryString("file_name");

    if(file_name !=null && file_name.toString().length>1){

        filenameobj = document.getElementById("file_name") 

        chosenfileobj = document.getElementById("chosen_file") 

        hashobj = document.getElementById("hash") 
        
        hashobj.style.display="block"; 
        filenameobj.style.display="block"; 
        chosenfileobj.style.display="block";
        chosenfileobj.innerHTML="当前选中的文件："+file_name;

        new_option = new Option(file_name,file_name);
        new_option.setAttribute("id",file_name);
        new_option.setAttribute("title","option");
        filenameobj.options.add(new_option); 


    }
}



function checkload() { 

    set_filechosen()

    set_optionselected("selected_hash")
    set_optionselected("author_name")
    set_optionselected("branch_name") 
    set_optionselected("selected_file") 
    set_optionselected("selected_sheet") 



}


function setvalue(form_id,select_id) {

    selectobj=document.getElementById(select_id)
 
    if(selectobj!=null){

        selected=selectobj.selectedIndex

        if (selected!=-1) {
        
            value=selectobj.options[selected].value

            var value_id=form_id+select_id

            valueobj=document.getElementById(value_id)

            if (valueobj!=null) {
            
                valueobj.value=value
            
            }
       }

   }        

}




function setpara(form_id){

    setvalue(form_id,"branch_name")

    setvalue(form_id,"author_name")

    setvalue(form_id,"selected_hash")

    setvalue(form_id,"file_name")

}

    
function showfilename(str){

    var xmlhttp;

    $.get("/xmlfile2",{"input_name":str},function(data){
        
        selectobj = document.getElementById("file_name");

        selectobj.options.length = 0;

        data = data.sort( function(a,b){ return a.length-b.length; })

        for ( key in data ) {
            new_option = new Option(data[key],data[key]);
            new_option.setAttribute("id",data[key]);
            new_option.setAttribute("title","option");
            selectobj.options.add(new_option); 
       }

        if (str.length==0 ) {
            document.getElementById("no_matchfile").style.display="none";
            document.getElementById("file_name").style.display="none";
        }
        else if ( data.length==0 ) {
            document.getElementById("no_matchfile").style.display="block";
            document.getElementById("file_name").style.display="none";
        }
        else {
            document.getElementById("no_matchfile").style.display="none";
            document.getElementById("file_name").style.display="block";
        } 

    });

}

