
# coding: utf-8

# importing required libraries
import os
import re

# extracting input and output directory information from run.sh file
#os.getcwd()+
with open('run.sh', 'r')as file:
    src = file.read()
run_list = src.split('./')
input_loc = run_list[1].strip()
output_loc_occ = run_list[2].strip()
output_loc_state = run_list[3].strip()

def find_index(header):
    '''
    To find the index of 'STATUS', 'OCCUPATIONAL NAME' and 'WORK STATE' from the header row.
    
    Arguments:
    header: The header row consisting of field names
    '''
    ind = []
    for e, i in enumerate(header):
        if len(ind)==3: continue
        if any(x in i for x in ['STATUS', 'SOC_NAME']): 
            ind.append(e)
        if all(x in i for x in ['STATE', 'WORK']):
            ind.append(e)
    return(ind)

def find_string(string, start, end, sym = '"'):
    '''
    To find the index of all occurances of a symbol in a given string.
    
    Arguments:
    string: input string
    start: where to start searching?
    end: where to end searching?
    sym: what symbol to look for?
    '''
    flag = True
    index = []
    while flag:
        index_op = string.find(sym, start, end)
        if index_op == -1: 
            flag = False
        else: 
            start = index_op+1
            index.append(index_op)
    return(index)

def clear_string(string, op = '"'):
    '''
    To remove the symbol and concatenate the rest of the string.
    
    Arguments:
    string: Input string
    op: Symbol to be removed from the string
    '''
    index = find_string(string, start = 0, end = len(string), sym = op)
    num_op = int(len(index)/2)
    print(index)
    index_rm = []
    for i in range(num_op):
        index_op = find_string(string, start = index[2*i], end = index[2*i+1], sym = ';')
        index_rm.extend(index_op)
    print(index_rm)
    string_part = []
    start = 0
    for i in range(len(index_rm)):
        end = (index_rm[i+1] if i < len(index_rm)-1 else len(string)-1) 
        string_br = [string[start:index_rm[i]], string[(index_rm[i]+1):end]]
        string_part.extend(string_br)
        start = end+1
    return(''.join(string_part))

def break_tie(list_sorted):
    '''
    To break the tie from the sorted list.
    
    Arguments:
    list_sorted: The sorted dictionary, mapping names to sorted certified total values
    '''
    ks = [i[0] for i in list_sorted[:10]]
    vals = [i[1] for i in list_sorted[:10]]
    ind = []
    for i in range(len(vals)):
        if (vals[i]-vals[i-1]) == 0: ind.append(i)
    if len(ind)>0:
        for i in range(len(ind)):
            if ks[ind[i]]<ks[ind[i]-1]:
                dummy = ks[ind[i]-1]
                ks[ind[i]-1] = ks[ind[i]]
                ks[ind[i]] = dummy
    return(ks, vals)

def extract_top(data, val):
    '''
    To extract the top (most frequent) field names.
    
    Arguments:
    data: The list of dictionaries of data
    val: The field of which top names are required
    '''
    data_list = [i[val] for i in data]
    val_dict_init = {}
    for i in data_list:
        val_dict_init[i] = val_dict_init.get(i,0)+1
    num_row = min(10, len(val_dict_init))
    top_val = sorted(val_dict_init.items(), key=lambda k: (-k[1],k[0]))[:num_row]
    top_vals = [i for i,_ in top_val]
    return(top_vals)

def extract_certified_data(data, val, top_val):
    '''
    To extract certified information about the top (most frequent) values.
    
    Arguments;
    data: The list of dictionary data
    val: The values of which the top values are required
    top_val: most frequent values of val field
    '''
    all_certified = [i for i in data if i['status'] == 'CERTIFIED']
    certified_val_records = [i for i in all_certified if i[val] in top_val]
    val_certified = [i[val] for i in certified_val_records]
    val_certified_dict = {}
    for v in val_certified:
        val_certified_dict[v] = val_certified_dict.get(v,0)+1
    val_certified_sorted = sorted(val_certified_dict.items(), key = lambda k: (-k[1],k[0]))
    top, values = break_tie(val_certified_sorted)
    perc_certified = [str(round(value/len(all_certified)*100, 1))+'%' for value in values]
    return (top, values, perc_certified)

# Read the data and extract the required information
with open(r''+os.getcwd()+'/'+input_loc, encoding="utf8") as soap:
    header = soap.readline() # read the header
    header = header.strip().split(';')
    req_index = find_index(header) # retrieve important indexes
    dict_index = {'status': req_index[0], 'title': req_index[1], 'state': req_index[2]}
    list_data = [] 
    for line in soap: # read rest of the file
        dict_data = dict.fromkeys(['title', 'status', 'state'])
        try:
            line_list= line.strip().split(';') 
            if len(line_list)!= len(header): # if the number of fields not equal to the number of header fields, clean the string
                line_list = clear_string(line).strip().split(';')
            for k in dict_data.keys():
                dict_data[k] = line_list[dict_index[k]]
            dict_data['title'] = re.findall('[^"]+', dict_data['title'])[0]
            list_data.append(dict_data) # append the data to a list
        except:
            continue

# Top occupational data
top, values, perc_certified = extract_certified_data(list_data, 'title', extract_top(list_data, 'title'))

#r''+os.getcwd()+
with open (output_loc_occ, 'w') as file:
    file.write('TOP_OCCUPATIONS;NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE \n')
    for i in range(len(top)):
        file.write((top[i]) +';' +str(values[i])+';'+str(perc_certified[i]) + '\n')

# Top states data
top, values, perc_certified = extract_certified_data(list_data, 'state', extract_top(list_data, 'state'))
#r''+os.getcwd()+
with open (output_loc_state, 'w') as file:
    file.write('TOP_STATES;NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE \n')
    for i in range(len(top)):
        file.write((top[i]) +';' +str(values[i])+';'+str(perc_certified[i]) + '\n')

