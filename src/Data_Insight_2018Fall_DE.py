
# coding: utf-8

# In[ ]:


#get_ipython().system('jupyter nbconvert --to script Data_Insight_2018Fall_DE.ipynb')

import os
#from os.path import dirname
with open(os.getcwd()+'\\run.sh', 'r')as file:
    src = file.read()
run_list = src.split('./')
input_loc = run_list[1].strip()
output_loc_occ = run_list[2].strip()
output_loc_state = run_list[3].strip()

def find_index(header):
    ind = []
    for e, i in enumerate(header):
        if len(ind)==3: continue
        if any(x in i for x in ['STATUS', 'SOC_NAME']): 
            ind.append(e)
        if all(x in i for x in ['STATE', 'WORK']):
            ind.append(e)
    return(ind)

def find_string(string, start, end, sym = '"'):
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
    index = find_string(string, start = 0, end = len(string), sym = op)
    num_op = int(len(index)/2)
    index_rm = []
    for i in range(num_op):
        index_op = find_string(string, start = index[2*i], end = index[2*i+1], sym = ';')
        #index_op = string.find(';', index[2*i], index[2*i+1])
        index_rm.extend(index_op)
    string_part = []
    start = 0
    for i in range(len(index_rm)):
        end = (index_rm[i+1] if i < len(index_rm)-1 else len(string)-1) 
        string_br = [string[start:index_rm[i]], string[(index_rm[i]+1):end]]
        string_part.extend(string_br)
        start = end+1
    return(''.join(string_part))


def break_tie(list_sorted):
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


with open(r''+os.getcwd()+'/'+input_loc, encoding="utf8") as soap:
    header = soap.readline()
    header = header.strip().split(';')
    req_index = find_index(header)
    dict_index = {'status': req_index[0], 'title': req_index[1], 'state': req_index[2]}
    list_data = [] 
    for line in soap:
        dict_data = dict.fromkeys(['title', 'status', 'state'])
        try:
            line_list= line.strip().split(';')
            if len(line_list)!= len(header): 
                line_list = clear_string(line).strip().split(';')
            for k in dict_data.keys():
                dict_data[k] = line_list[dict_index[k]]
            list_data.append(dict_data)
        except:
            continue


# ## Title

title_list = [i['title'] for i in list_data]
title_dict_init = {}
for i in title_list:
    title_dict_init[i] = title_dict_init.get(i, 0)+1
num_row = min(10, len(title_dict_init))
top_titles = sorted(title_dict_init.items(), key = lambda k: k[1], reverse=True)[:num_row]
top_titles = [i for i,_ in top_titles]
certified = [i for i in list_data if (i['status'] == 'CERTIFIED')&(i['title'] in top_titles)]
title = [i['title'] for i in certified]
title_dict = {}
for t in title:
    if t == '': continue
    title_dict[t] = title_dict.get(t, 0)+1
title_sorted = sorted(title_dict.items(), key = lambda k: k[1], reverse = True)
ks, vals = break_tie(title_sorted)
all_certified = [i for i in list_data if i['status'] == 'CERTIFIED']
perc_certified = [str(round(val/len(all_certified)*100, 1))+'%' for val in vals]

with open (r''+os.getcwd()+'/'+output_loc_occ, 'w') as file:
    file.write('TOP_OCCUPATIONS; NUMBER_CERTIFIED_APPLICATIONS; PERCENTAGE \n')
    for i in range(len(ks)):
        file.write(str(ks[i]) +';' +str(vals[i])+';'+str(perc_certified[i]) + '\n')

# ## States
states = [i['state'] for i in list_data]
states_dict = {}
for s in states:
    if len(s) == 0: continue
    states_dict[s] = states_dict.get(s,0)+1
states_dict = sorted(states_dict.items(), key = lambda k: k[1], reverse=True)
num_row = min(10, len(states_dict))
top_states = [i for i,_ in states_dict[:num_row]]
certified_states = [i for i in list_data if (i['state'] in top_states)&(i['status'] == 'CERTIFIED')]
top_certified_states = [i['state'] for i in certified_states]
top_certified_states_dict = {}
for i in top_certified_states:
    top_certified_states_dict[i] = top_certified_states_dict.get(i,0)+1
top_certified_states_dict = sorted(top_certified_states_dict.items(), key = lambda k: k[1], reverse=True)
state, vals = break_tie(top_certified_states_dict)
perc_state = [str(round(val/len(all_certified)*100, 1))+'%' for val in vals]

with open (r''+os.getcwd()+'/'+output_loc_state, 'w') as file:
    file.write('TOP_STATES; NUMBER_CERTIFIED_APPLICATIONS; PERCENTAGE \n')
    for i in range(len(state)):
        file.write(str(state[i]) +';' +str(vals[i])+';'+str(perc_state[i]) + '\n')

#with open(output_filename, 'w') as file:
