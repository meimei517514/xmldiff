from flask import Flask,request,abort,redirect,render_template,url_for,jsonify
from basecode.xmlrefer import *
from basecode.xmldiff import *
from basecode.xmlfile import *
from git import *
import re

app = Flask(__name__)

app.config["SECRET_KEY"] = "hard to guess"


@app.errorhandler(404)
def error_page_define(e):
    return "hail hydra!!"

  
@app.route("/xmlrefer",methods=["GET","POST"])
def xmlrefer():

    upgrade_info =request.values.get("upgrade")

    file_selected=request.values.get("file_name",xml_names[0]) 

    sheet_selected=request.values.get("sheet_name")

    sheet_namedict,sheet_data = get_sheetinfo(file_selected,sheet_selected,xml_paths,upgrade_info) 

    sheet_data=get_workbookdata(sheet_data,file_selected) 

    return render_template("xmlrefer.html",xml_names=xml_names,sheet_namedict=sheet_namedict,file_selected=file_selected,sheet_data=sheet_data)


@app.route("/xmldiff",methods=["GET","POST"])
def xmldiff():	
 
    upgrade_info = request.values.get("upgrade_info")

    author_name = request.values.get("author_name")

    branch_name = request.values.get("branch_name")

    branch_list = get_gitbranch(branch_name)

    hash_list,hash_info,author_name = get_gitinfo(upgrade_info,author_name,branch_name)

    selected_hash = request.values.get("selected_hash",hash_list[0])

    selected_file = request.values.get("selected_file")

    selected_sheet = request.values.get("selected_sheet")

    file_namelist,sheet_namelist,author,other_diff,maped_diff=get_gitdiff(selected_hash,selected_file,selected_sheet,hash_list)

    return render_template("xmldiff.html",branch_list=branch_list,file_namelist=file_namelist,sheet_namelist=sheet_namelist,hash_info=hash_info,author_name=author_name,author=author,other_diff=other_diff,maped_diff=maped_diff)

@app.route("/xmlfile",methods=["GET","POST"])
def xmlfile():

    upgrade_info = request.values.get("upgrade_info")

    file_name = request.values.get("file_name")

    branch_name = request.values.get("branch_name")

    branch_list = get_gitbranch(branch_name)

    hash_list,hash_info= get_fileinfo(upgrade_info,branch_name,file_name)

    selected_hash = request.values.get("selected_hash")

    selected_file = request.values.get("selected_file")

    selected_sheet = request.values.get("selected_sheet")

    file_namelist,sheet_namelist,author,other_diff,maped_diff=get_gitdiff(selected_hash,selected_file,selected_sheet,hash_list)

    return render_template("xmlfile.html",branch_list=branch_list,file_namelist=file_namelist,sheet_namelist=sheet_namelist,hash_info=hash_info,author=author,other_diff=other_diff,maped_diff=maped_diff)

@app.route("/xmlfile2",methods=["GET","POST"])
def xmlfile2():

    input_name = request.values.get("input_name")

    match_file =get_matchfile(input_name)

    return jsonify(match_file)

if __name__ == "__main__":
    app.run(threaded=True,host="100.84.74.126",debug=True)
    
