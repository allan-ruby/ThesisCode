import pandas as pd


mcg_metabolite_worksheet = pd.read_csv(r'C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\KristenResults\results\mummichog\tsv\mcg_metabolite_worksheet_mummichog.tsv',sep='\t')

def dictionary_sort(dataframe,col_identifier):
    working_dict = {}
    for index, row in dataframe.iterrows():
        key = row[col_identifier]
        if key not in working_dict:
            working_dict[key] = row
        else:
            current_list =working_dict[key]
            current_list.append(row)
            working_dict[key] = current_list
    return working_dict
metab_dict = dictionary_sort(mcg_metabolite_worksheet,0)
pathway_dict = dictionary_sort(mcg_metabolite_worksheet,5)

#for index,row in mcg_metabolite_worksheet.iterrows():
#    if row[0] not in metab_dict:
#        metab_dict[row[0]] = [row[1:]]
#    else:
#        current_list = metab_dict[row[0]]
#        current_list.append(row[1:])
#        metab_dict[row[0]] = current_list
#for index, row in mcg_metabolite_worksheet.iterrows():
#    if row[5] not in pathway_dict:
#        pathway_dict[row[5]] = [row]
#    else:
#        current_list = pathway_dict[row[5]]
#        current_list.append(row)
#        pathway_dict[row[5]] = current_list
#    