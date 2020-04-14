import pandas as pd
import pickle
import pubchempy as pcp
from rdkit import Chem, DataStructs
import numpy as np
from PredRetDatabaseProcessor import mol_prop_gen, fps_plus_mw
from metabolic_map_intake import dictionary_sort
import timeit

def write_list_to_csv(List,output_file):
    
    df = pd.DataFrame(List)
    df.to_csv(output_file)

def generate_data(name,inchi,rt='null'):
    
    cmpd = pcp.get_compounds(inchi,'inchi')
    cmpd = pcp.get_compounds(inchi,'inchi')
    props = cmpd[0].to_dict(properties=['cactvs_fingerprint',
                        'isomeric_smiles', 'xlogp', 'rotatable_bond_count','charge','complexity',
                        'exact_mass','fingerprint'])
    smiles=props['isomeric_smiles']
    props['mol']=Chem.MolFromSmiles(smiles)
    props['RT'] = rt
    props['Name'] = name
#    props['System'] = row['System']
    desc = np.array(fps_plus_mw(props['mol']))
    descdf = pd.DataFrame(desc)
    descdf = descdf.T
#    descdf.reindex([index])
    newdf=pd.DataFrame(props,index=[0])
    finaldf=pd.concat([descdf,newdf],axis=1)
    return finaldf
    
def Take_In_RT_Markers(file):
    df = pd.read_csv(file)
    list_data_df = []
    for index,row in df.iterrows():
        name = row[0]
        inchi = row[1]
        rt = row[2]
        print(name,inchi,rt)
        list_data_df.append(generate_data(name,inchi,rt))
    return pd.concat(list_data_df)   

def create_training_set(df_fem_long,output):
    df_list = []
    for i in range(len(df_fem_long)):
        print('On index {}'.format(i))
        first_part= df_fem_long.iloc[[i]]
        first_part.columns=col_A
        first_part = first_part.reset_index()
        for i2 in range(i+1,len(df_fem_long)):
    #        print(i2)
            entry=[]
            second_part = df_fem_long.iloc[[i2]]
            second_part.columns=col_B
            second_part = second_part.reset_index()
            entry = [first_part,second_part]
            df = pd.concat(entry,axis=1)
            df_list.append(df)
    train_df = pd.concat(df_list,ignore_index=True)
    RT_status = []
    for index,row in train_df.iterrows():
    #    print(row['ART'],row['BRT'])
        a_RT = float(row['ART'])
        b_RT = float(row['BRT'])
        if a_RT == b_RT:
            RT_status.append('error')
        elif a_RT > b_RT:
            RT_status.append(0)
        elif b_RT > a_RT:
            RT_status.append(1)
        else:
            RT_status.append('error')
    train_df['Result'] = RT_status
    for index,row in train_df.iterrows():
        if row['Result'] == 'error':
            train_df = train_df.drop(index)
    # train_df =train_df.drop(['ART','BRT','AName','BName','index','Amol','Bmol','Aisomeric_smiles','Bisomeric_smiles','ASystem','BSystem','Afingerprint','Bfingerprint','Acactvs_fingerprint','Bcactvs_fingerprint'],axis=1)
    train_df = train_df.fillna(0)

    train_df.to_csv(output)
    return train_df     
def Create_A_B_Columns(complete_DF,col_string):
    col_list = []
    for index,col in enumerate(complete_DF.columns):
        if index < 159:
           col_list.append(col_string + str(col))
        else:
            col_list.append(col_string + col)
    return col_list
        


file_path_to_file = r'C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\pickles\mummichog_rt_features.p'
mol_characteristics = pickle.load(open(file_path_to_file,'rb'))
mol_characteristics = mol_characteristics.drop(['System'],axis=1)
rt_file = Take_In_RT_Markers(r'C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\csvfiles\TemplateCompounds.csv')


model = pickle.load( open(r"C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\pickles\RFClassifier.pickle", "rb" ) )
rt_list = []
col_A = Create_A_B_Columns(mol_characteristics,'A')
col_B = Create_A_B_Columns(rt_file,'B')
rt_file.columns = col_B
mol_characteristics.columns = col_A
for index,row in rt_file.iterrows():
    rt = row['BRT']
    print(rt)
    rt_list.append(rt)
mol_characteristics.columns = col_A
mol_characteristics = mol_characteristics.reset_index()
mol_characteristics = mol_characteristics.drop(['index'],axis=1)
list_of_approved_cmpds = []
list_of_unapproved_cmpds = []
list_of_unsure_cmpds = []


mcg_metabolite_worksheet = pd.read_csv(r'C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\KristenResults\results\mummichog\tsv\mcg_metabolite_worksheet_mummichog.tsv',sep='\t')
metab_dict = dictionary_sort(mcg_metabolite_worksheet,0)
pathway_dict = dictionary_sort(mcg_metabolite_worksheet,5)
test_list = []
for index,row in mol_characteristics.iterrows():
    test_name = row['AName']
    if test_name in metab_dict.keys():
        test_list.append(test_name)
    print('On index {}'.format(index))
    df_list = []
    for i in range(len(rt_file)-1):
        entry = []
        entry = [mol_characteristics.iloc[[index]].reset_index(),rt_file.iloc[[i]].reset_index()]
        df = pd.concat(entry,axis=1)
        df_list.append(df)
    essential_df = pd.concat(df_list,ignore_index=True)
    essential_df = essential_df.fillna(0)
    actual_rt = row['ART']
    essential_df = essential_df.drop(['ART','BRT','AName','BName','index','Amol','Bmol','Aisomeric_smiles','Bisomeric_smiles','Afingerprint','Bfingerprint','Acactvs_fingerprint','Bcactvs_fingerprint'],axis=1)
    
    predictions = list(model.predict(essential_df))
    prob_A = list(model.predict_proba(essential_df))
    end_range = 100.0
    beginning_range = 0.00
    for index,result in enumerate(predictions):
        rt = rt_list[index]
        if prob_A[index][0] > .49 and prob_A[index][0] < .51:
            break
        if result == 1 and beginning_range < rt < end_range:
            end_range = rt
        if result == 0 and   end_range > rt > beginning_range:
            beginning_range = rt
    if beginning_range == 0.00 and end_range == 100.0 and test_name not in list_of_unsure_cmpds:
        list_of_unsure_cmpds.append(test_name)
    elif beginning_range < actual_rt < end_range and test_name not in list_of_approved_cmpds:
        list_of_approved_cmpds.append(test_name)
    elif not beginning_range < actual_rt < end_range and test_name not in list_of_unapproved_cmpds:
        list_of_unapproved_cmpds.append(test_name)
    print('Start range of RT is {} and end range of RT is {} for {}'.format(beginning_range,end_range,test_name))    
total = len(list_of_approved_cmpds) + len(list_of_unapproved_cmpds) + len(list_of_unsure_cmpds)
print('False positves removed {}, perventage is {}'.format(len(list_of_unapproved_cmpds),(len(list_of_unapproved_cmpds)/total) * 100))
write_list_to_csv(list_of_approved_cmpds,'approved.csv')
write_list_to_csv(list_of_unapproved_cmpds,'unapproved.csv')
write_list_to_csv(list_of_unsure_cmpds,'unsure.csv')

def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3

print(intersection(list_of_approved_cmpds,list_of_unapproved_cmpds))
print(intersection(list_of_approved_cmpds,list_of_unsure_cmpds))
print(intersection(list_of_unapproved_cmpds,list_of_unsure_cmpds))




