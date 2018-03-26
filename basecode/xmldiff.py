### -*- coding: UTF-8 -*-:
from basecode.xmlaccess import *
from git import *
from datetime import datetime
import re,copy,os.path


path_sum=parse_path()

project_path = path_sum["project_path"]

git_path = path_sum["git_path"]

repo=Repo.init(git_path)


def get_gitbranch(branch_name):

    #获取活跃分支列表
    branch_list=repo.git.branch("--list").split("\n")

    current_branch=[ branch.strip("* ") for branch in branch_list if "*" in branch][0]

    #print current_branch,branch_name
    if branch_name!=current_branch:

        repo.git.fetch("--all")
        repo.git.reset("--hard","origin/"+current_branch)
        repo.git.checkout(branch_name)
        repo.git.pull()

    branch_list=repo.git.branch("-a","-r").split("\n")

    branch_list=[ branch.strip(" origin/") for branch in branch_list  ]

    branch_list=[ branch for branch in branch_list if get_usefulbranch(branch) ]

    valid_branch=["master","gangtai","mailiang"]

    valid_branch.extend(branch_list)
 
    return valid_branch


def get_usefulbranch(branch):

    #判断分支是否是活跃分支
    current_date=datetime.now()

    last_slice=branch.rfind("-")

    if last_slice>11:

        branch_date=branch[last_slice+1:]

        branch_date="20"+branch_date if branch_date.isdigit() and len(branch_date)==6 else "20160522"

        #打的分支名不符合年月日的规则，需要特殊处理一下
        branch_date=branch_date if branch_date!="20180942" else "20180326"

        branch_date=datetime.strptime(branch_date,'%Y%m%d')

        gap_days=(current_date-branch_date).days

        return True if gap_days<=50 else False
    else:
        return False

        


def get_gitinfo(upgrade_info,author_name,branch_name):

    #获取提交的hash列表,作者列表
    if upgrade_info :
        repo.git.fetch("--all")
        repo.git.reset("--hard","origin/"+branch_name)
        repo.git.pull()

    author_name="" if author_name=="all" or not author_name else author_name

    author_name= "--author="+author_name

    commit_hash,commit_list,commit_author=get_lastcommit(author_name) 

    return commit_hash,commit_list,commit_author


def get_lastcommit(author_name):

    #循环查找该分支最近的提交记录,找到记录或者时间太长就跳出循环
    days=50

    while True:

        log_time='--after={%s,days,ago}'%(days)
        
        commit_message=repo.git.log('--pretty=format:%cn:%s',log_time,author_name)

        if commit_message or days>168:

            commit_message=[ message.strip() for message in commit_message.split("\n")]

            commit_hash=repo.git.log('--pretty=format:%H',log_time,author_name).split("\n")

            commit_list=zip(commit_hash,commit_message)

            commit_author=repo.git.log('--pretty=format:%an',log_time).split("\n")

            commit_author=list(set(commit_author)) 

            return commit_hash,commit_list,commit_author
        else:
            days=days+7




def get_gitdiff(selected_hash,selected_file,selected_sheet,hash_list):

    #获取当次提交改变的文件列表及DIFF
    if selected_hash:
        selected_file,path_name,c_type,file_name=get_baseinfo(selected_hash,selected_file,hash_list)

    if selected_file:

        #git.show指令要求文件存在，如果文件当前不存在，找到文件被删除的记录，将文件回滚
        if not os.path.exists(path_name):

            delected_hash=repo.git.rev_list("-n",1,"HEAD","--",path_name)

            repo.git.checkout(delected_hash+"^",path_name)

        diff_detail=repo.git.show(selected_hash,path_name)

        sheet_name,author,other_diff,maped_diff=get_filediff(selected_hash,selected_sheet,diff_detail,c_type,path_name)

        sheet_name=[ (selected_file,name) for name in sheet_name ]

        return file_name,sheet_name,author,other_diff,maped_diff

    else:

        author=repo.git.show(selected_hash) if selected_hash else u"该分支最近半年无变更内容"

        return [],[],author,[],{}



def get_baseinfo(selected_hash,selected_file,hash_list):

    #准备需要的数据，检查文件名字是否合法，获取改变的文件名字、路径、改变模式等等
    #print selected_hash or "None"

    file_info=repo.git.show(r"--pretty=""","--name-status",selected_hash)

    file_info=file_info.split("\n")

    file_cmode=[ line[:line.find("\t")] for line in file_info if line ]

    file_path=[ line[line.find("\t")+1:].strip() for line in file_info if line]

    file_name=[ path[ path.rfind("/")+1:] for path in file_path if path ] 

    file_path=[ project_path+"/"+path for path in file_path if path]

    file_path=dict(zip(file_name,file_path))

    file_cmode=dict(zip(file_name,file_cmode))

    selected_file =  ( selected_file if selected_file in file_name else file_name[0] ) if file_name else None

    path_name=file_path[selected_file] if selected_file else None

    c_type=file_cmode[selected_file] if selected_file else None

    return selected_file,path_name,c_type,file_name




def get_filediff(selected_hash,selected_sheet,diff_detail,c_type,path_name):

    #只有xml文件的M或MM状态才处理，其它类型文件不处理
    #print diff_detail

    da_word={"A":path_name+"  newly add","D":path_name+" Delected"}
 
    slice_index= diff_detail.find("\ndiff --git")+1 or diff_detail.find("\ndiff --cc")+1 

    author=diff_detail[:slice_index]

    file_diff=diff_detail[slice_index:]

    other_diff= [file_diff]

    if ".xml" in path_name and "M" in c_type:

        row_seq=get_changerow(file_diff) 

        selected_sheet,sheet_name,maped_diff=get_mapediff(selected_hash,selected_sheet,path_name,row_seq)

        other_diff=[u"都是些无用的变更，表格的数据没变，莫慌"] if not sheet_name or not maped_diff else []

        return sheet_name,author,other_diff,maped_diff
       
    else:

        other_diff=[da_word[c_type]] if c_type in da_word.keys()  else other_diff

        return [],author,other_diff,{}



def get_mapediff(selected_hash,selected_sheet,path_name,row_seq):

    #对获得的变更行进行处理，获得行的完整数据，并将所有的变更行格式化
    old_row=[ (row,change_info) for change_info in row_seq for row in change_info["old"]]

    new_row=[ (row,change_info) for change_info in row_seq for row in change_info["new"]]

    sheet_cinfo={}

    #print selected_hash
    repo.git.checkout(selected_hash,path_name)

    new_sheetname,new_sheetdata=get_sheetname(path_name,new_row,sheet_cinfo) 

    pre_hash=repo.git.log(selected_hash+"^","-1","--pretty=%H")

    #print pre_hash

    repo.git.checkout(pre_hash,path_name)

    old_sheetname,old_sheetdata=get_sheetname(path_name,old_row,sheet_cinfo)

    new_sheetname.extend(old_sheetname)

    sheet_name=list(set(new_sheetname))

    selected_sheet= selected_sheet or  ( sheet_name[0] if sheet_name else None )

    row_cinfo= sheet_cinfo[selected_sheet] if selected_sheet and sheet_cinfo else None

    maped_diff=get_data(selected_sheet,row_cinfo,new_sheetdata,old_sheetdata)  if selected_sheet else {}  

    return selected_sheet,sheet_name,maped_diff



def get_sheetname(path_name,row_info,sheet_cinfo):

    #获得有内容改变的子表名字，以及子表数据 
    sheet_range,sheet_data=get_sheetrange(path_name)

    sheet_info=[ locate_sheet(sheet_range,row_seq) for row_seq in row_info]
    
    sheet_info=[ name_info for name_info in sheet_info if name_info]

    sheet_name=[ name_info[0] for name_info in sheet_info ]

    for name,row_seq in sheet_info:

        c_info=row_seq[1]

        sheet_cinfo[name]= sheet_cinfo[name] if name in sheet_cinfo else []

        if c_info not in sheet_cinfo[name]:

            sheet_cinfo[name].append(c_info) 
 
    return sheet_name,sheet_data




def locate_sheet(sheet_range,row_seq):

    #定位改变的行属于哪个字表
    row=row_seq[0]

    for name,name_range in sheet_range.items():

        start=name_range[0]

        end=name_range[1]

        if row>=start and row<end:

            return name,row_seq
 



def get_data(selected_sheet,row_cinfo,new_sheetdata,old_sheetdata):

    #根据改变的行获取行完整数据 
    new_data=new_sheetdata[selected_sheet] if selected_sheet in new_sheetdata else []

    new_header=get_sheet(selected_sheet,new_data,row_cinfo,"new")

    old_data=old_sheetdata[selected_sheet] if selected_sheet in old_sheetdata else []

    old_header=get_sheet(selected_sheet,old_data,row_cinfo,"old")

    maped_diff=map_truediff(row_cinfo,new_header)

    return maped_diff


def get_sheet(selected_sheet,sheet_data,row_cinfo,c_type):

    #将变更的数据替换成完整的行，并且拿到子表的表头
    if sheet_data:

        start_row=sheet_data[0]

        sheet_detail=sheet_data[1]

        end_row=start_row+len(sheet_detail)

        sheet_area=(start_row,end_row)

        row_refer,row_area=get_rowinfo(sheet_data)

        row_fulldata=get_sheetdata(sheet_detail)

        row_list=[ row for info in row_cinfo for row in info[c_type] ]

        crow_data=[ extract_rowdata(selected_sheet,row_refer,row_fulldata,row,sheet_area) for row in row_list]

        crow_list=sorted([ reference_row for reference_row,row_data in crow_data])

        first_crow=crow_list[0] if crow_list else 10

        crow_data=dict(zip(row_list,crow_data))

        change_info=copy.deepcopy(row_cinfo)

        for index,info in enumerate(change_info):

            for key,row in enumerate(info[c_type]):
                if crow_data[row][1]:
                    row_cinfo[index][c_type][key]=crow_data[row]
                else:
                    row_cinfo[index][c_type].remove(row)

        sheet_header=get_header(row_fulldata)

        #如果是新增的sheet或者header本身有变化就不用加header了
        sheet_header=sheet_header if sheet_header and first_crow>=len(sheet_header) else [] 

        return sheet_header

       



def extract_rowdata(selected_sheet,row_refer,row_fulldata,row,sheet_area):

    #查找行数对应在子表中的相对行，返回完整的行数据
    reference_row=row_refer[row] if row in row_refer else row

    fulldata_len=len(row_fulldata)-1

    row_data=copy.deepcopy(row_fulldata[reference_row])  if reference_row<=fulldata_len  else [ selected_sheet] 

    #print row,reference_row,row_data

    return (reference_row,row_data)




def get_header(row_fulldata):

    #获得子表的表头
    row_firstcell=[ line[0] for line in row_fulldata]

    for key,cell in enumerate(row_firstcell):

        if key>=2:
 
            next_cell=row_firstcell[key+1] if key!=len(row_firstcell)-1 else cell

            if (cell and not any(row_firstcell[key+1:key+11]) ) or (not cell.isalnum() and any(alp.isalnum() for alp in next_cell)):

                header=copy.deepcopy(row_fulldata[:key+1])

                return header




def map_truediff(row_cinfo,sheet_header):

    #将最终要显示的数据格式化
    diff_data=[]

    for info in row_cinfo:

        #如果某个子表的数据是空的，row_cinfo的数据在之前是没有处理好的。先在这里忽略掉没有处理好的数据，以后再看看有什么好办法
        reference_row=[ row_list[0] for row_list in info["new"] if type(row_list)==tuple]

        reference_row=[ row_list[0] for row_list in info["old"] if type(row_list)==tuple] if not reference_row else reference_row

        old_origin=[ row_list[1] for row_list in info["old"] if type(row_list)==tuple]
        
        new_origin=[ row_list[1] for row_list in info["new"] if type(row_list)==tuple]

        #print "diff_data:--------", old_origin,new_origin
        
        old_data=[row for row in old_origin if row not in new_origin and any(row)]
                        
        new_data=[row for row in new_origin if row not in old_origin and any(row)]

        if old_data or new_data: 

            start_row=str(reference_row[0]) if reference_row else "0"

            desc_row=[["","@@ change in row:"+start_row+"@@"]]

            diff_data.extend(desc_row)

        for row in old_data:
            row.insert(0,"---")

        for row in new_data:
            row.insert(0,"+++")

        diff_data.extend(old_data)
        diff_data.extend(new_data)

    if sheet_header and diff_data:

        for row in sheet_header:

            row.insert(0,"")

        sheet_header.extend(diff_data)

        diff_data=sheet_header

    return diff_data





def get_changerow(file_diff):

    #分析diff,找到发生变更的行ID
    diff_sliced=slice_diff(file_diff,"@@(.+)@@")

    row_changed=[]

    #分割后的diff列表，第一个值是文件的地址信息，无效
    for diff in diff_sliced[1:]:

        #print diff
        row_info=get_rowseq(diff)
        #print row_info

        if row_info and any(row_info.values()):

            row_changed.append(row_info)

    return row_changed   



    
def slice_diff(diff_detail,re_expression):

    #根据表达式来切割diff
    slice_index=[diff.start() for diff in re.finditer(re_expression,diff_detail)]

    diff_len=len(diff_detail)

    slice_index.insert(0,0)

    slice_index.append(diff_len)

    sliced_diff=[diff_detail[index:slice_index[key+1]] for key,index in enumerate(slice_index) if index!=diff_len]

    return  sliced_diff




def get_rowseq(diff):

    #获得每部分diff中有变更的行信息,两重检查：一是去除表格实际内容没变的diff，二是去掉diff中新旧内容前面的无用行
    '''
    if "43000026" in "".join(diff):
    
    '''

    diff_list=diff.split("\n")

    equal_tag=check_equal(diff_list)

    if not equal_tag:

        old_origin=get_validrow(diff_list,"-")

        new_origin=get_validrow(diff_list,"+")

        old_row=sorted([ key for key,value in old_origin.items() if value not in new_origin.values()] )

        new_row=sorted([ key for key,value in new_origin.items() if value not in old_origin.values()] )

        row_info={"old":old_row,"new":new_row} 

        #print diff,row_info

        return row_info


def check_equal(diff_list):

    #如果diff中行的新旧信息其实是一样的，就不算有变更
    old_diff=get_cleandiff(diff_list,"+")

    new_diff=get_cleandiff(diff_list,"-")

    equal_tag=(old_diff==new_diff )
    
    return equal_tag



def get_cleandiff(diff_list,style):

    #提取变更前后的数据
    ctag={"-":"+","+":"-"}

    clean_diff=filter((lambda x:not x.startswith(style)),diff_list)

    clean_diff=[ get_datare(line) for line in clean_diff]

    return clean_diff


def get_datare(line):
    
    #去除无用的标签数据，只获取cell数据
    data_re=re.search(">([^>]+)</",line) 

    cell_data=data_re.group(1) if data_re else "" 

    return cell_data



def get_validrow(diff_list,style):

    #分析diff，获得真正涉及到表格内容的变更行
    ctag={"-":"+","+":"-"}
    
    row_info=diff_list[0]

    #print row_info

    start_row=get_startrow(row_info,style)

    filtered_diff=[ line for line in diff_list if not line.startswith(ctag[style]) ] 

    row_index=[ key for key,line in enumerate(filtered_diff) if any( tag in line for tag in ["<Row","<Worksheet"] ) ]

    row_index.insert(0,0)

    include_row=[ filtered_diff[index:row_index[key+1]] if key!=len(row_index)-1 else filtered_diff[index:] for key,index in enumerate(row_index) ]

    row_data=[ get_celldata(row) for row in include_row]

    include_row=[ "\n".join(row) for row in include_row]

    #实际的行index会差1,因为第一行就是@@里面的数字
    row_index=[ start_row+re_row if key==0 else start_row+re_row-1 for key,re_row in enumerate(row_index) ]

    data_zip=zip(row_index,include_row,row_data)

    valid_tag=[ "/Row>","\n"+style+"    <Cell","\n"+style+"    <Worksheet","\n     <Cell"]

    valid_row=dict([ (key,row) for key,diff,row in data_zip if any( tag in diff for tag in valid_tag ) ] )

    #print valid_row

    return valid_row 




def get_startrow(row_info,style):

    #根据新旧标志，获得diff的起始行
    start=row_info.find(style)+1

    end=row_info.find(",",start)

    row_index=int(row_info[start:end])
    
    #print row_info,start,end,row_index

    return row_index
   



def get_sheetrange(path_name):

    #获得文件每个分页的行范围
    xmlfile_list=open_xml(path_name)
    
    sheet_name=[ re.search("\"(.*)\"",line).group(1) for line in xmlfile_list if "Worksheet " in line]

    sheet_start=[ key+1 for key,line in enumerate(xmlfile_list) if "Worksheet " in line]

    sheet_end=[ key+1 for key,line in enumerate(xmlfile_list) if "Worksheet>" in line]

    sheet_area=list(zip(sheet_start,sheet_end))

    sheet_range=dict(zip(sheet_name,sheet_area))

    sheet_data=[ (start,xmlfile_list[start:end]) for start,end in sheet_area]

    sheet_data=dict(zip(sheet_name,sheet_data))

    return sheet_range,sheet_data




def get_rowinfo(sheet_list):

    #获得每行对应的真实行ID及范围
    start=sheet_list[0]

    sheet_info=sheet_list[1]

    row_range=get_rowrange(start,sheet_info)

    row_refer=dict( [ (row,key) for key,(start,end) in enumerate(row_range) for row in range(start,end+1) ] )

    row_area=dict( [ (row,(start,end)) for key,(start,end) in enumerate(row_range) for row in range(start,end+1) ] )

    return row_refer,row_area




def get_rowrange(start,sheet_info):

    #获得每行的行范围
    
    row_start=[ start+key+1  for key,line in enumerate(sheet_info) if "<Row" in line ]
    
    row_end=[ start+key+1  for key,line in enumerate(sheet_info) if "/Row>" in line  or ( "<Row" in line and "/>" in line)]
 
    row_range=zip(row_start,row_end)

    #print row_range

    return row_range



if __name__=="__main__":
    pass

