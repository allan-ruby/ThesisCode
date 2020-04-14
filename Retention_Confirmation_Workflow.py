import pandas as pd
from rdkit import Chem
import pubchempy as pcp
import numpy as np
from PredRetDatabaseProcessor import fps_plus_mw
import pickle
import tkinter as tk
import xlwings as xw
from datetime import datetime

def write_list_to_csv(List,output_file):
    
    df = pd.DataFrame(List)
    df.columns = ['Name','Low Range','High Range','Actual Retention Time']
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
            print(i2)
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
        print(row['ART'],row['BRT'])
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
    train_df =train_df.drop(['ART','BRT','AName','BName','index','Amol','Bmol','Aisomeric_smiles','Bisomeric_smiles','ASystem','BSystem','Afingerprint','Bfingerprint','Acactvs_fingerprint','Bcactvs_fingerprint'],axis=1)
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

def xl_write(statement):
    wb = xw.Book('Interface.xlsm')
    sht = wb.sheets[0]
    sht.range("B15").clear_contents()
    sht.range("B15").value = statement
    time.sleep(.5)
    
def Join_Mummichog_Results_Retention_Times(filedir):
    results = pd.read_csv(filedir + 'results.tsv',sep='\t',encoding = "utf-8")
    mummichog =filedir + 'mummichog\\tsv\\_tentative_featurematch_mummichog.tsv'
    mummichogreadings = pd.read_csv(mummichog,sep='\t')
    compound_list = []
    mzlist = []
    for index,row in mummichogreadings.iterrows():
        if row['name'] not in compound_list:
            compound_list.append([row['name'],float(row['m/z'])])
    id_df = pd.DataFrame(compound_list,columns=['Compound Name','mzmed'])
    running_match_list = []
    #col1 = id_df.columns
    #col2 = results.columns
    #final_columns = col1+ col2
    for index,row in id_df.iterrows():
        print('On {} of {}'.format(index + 1,len(id_df)))
        for index,result_row in results.iterrows():
            threshold = .1
            low = float(row['mzmed'] - threshold)
            high = float(row['mzmed'] + threshold)
            if low < result_row['mzmed'] < high:
                df = pd.concat([row,result_row])
                df = df.transpose()
    #                df = df.reset_index()
                running_match_list.append(df)
    final_df = pd.concat(running_match_list,axis=1)
    final_df = final_df.transpose()
    
    final_df.to_csv(filedir + 'RT_Folder\\mummichog_results_with_retention_times.csv')
    return final_df

def Join_Mummichog_Matches_Molecular_Features(result_df,file_dir):
    
    # result_df = result_df.drop(['Unnamed: 0'], axis=1)
    running_cmpd_list = []
    for index,row in result_df.iterrows():
        if index == 0:
            name = row['Compound Name']
            # print(name)
            if name not in running_cmpd_list:
                running_cmpd_list.append(name)
    #            inchi = row['InChI']
                cmpd = pcp.get_compounds(name,'name')
                props = cmpd[0].to_dict(properties=['cactvs_fingerprint',
                            'isomeric_smiles', 'xlogp', 'rotatable_bond_count','charge','complexity',
                            'exact_mass','fingerprint'])
                smiles=props['isomeric_smiles']
                props['mol']=Chem.MolFromSmiles(smiles)
                props['RT'] = row['rtmin']
                props['Name'] = name
                props['System'] = 'xcms'
                desc = np.array(fps_plus_mw(props['mol']))
                descdf = pd.DataFrame(desc)
                descdf = descdf.T
                descdf.reindex([index])
                newdf=pd.DataFrame(props,index=[index])
                finaldf=pd.concat([descdf,newdf],axis=1)
            else:
                print('cmpd already queried')
        #            print('test')
        else:
            name = row['Compound Name']
            if name not in running_cmpd_list:
                running_cmpd_list.append(name)
                try:
                    cmpd = pcp.get_compounds(name,'name')
                except:
                    print('line bypassed')
                    pass
                try:
                    props = cmpd[0].to_dict(properties=['cactvs_fingerprint','isomeric_smiles', 'xlogp', 'rotatable_bond_count','charge','complexity','exact_mass','fingerprint'])
                except:
                    print('line bypassed')
                    pass
        #        name = row['Name']
                smiles=props['isomeric_smiles']
                props['mol']=Chem.MolFromSmiles(smiles)
                props['RT'] = row['rtmin']
                props['Name'] = name
                props['System'] = 'xcms'
                newdf=pd.DataFrame(props,index=[index])
                desc = np.array(fps_plus_mw(props['mol']))
                cols=range(len(desc))
                descdf=pd.DataFrame(desc)
                descdf = descdf.T
                descdf.index = [index]
        #        descdf = descdf.T
        #        descdf = pd.DataFrame(descdf, index=[index])
                interdf = pd.concat([descdf,newdf],axis=1)
                finaldf = finaldf.append(interdf)
            else:
                print('cmpd already queried')
            print('on index ' + str(index+1) + ' of ' + str(len(result_df)))
    
    finaldf.to_pickle(file_dir + 'RT_Folder\\mummichog_rt_features.p')
    return finaldf

def Run_Model_On_Punitive_Matches(mol_characteristics,rt_file,model_dir,file_dir):
    
    mol_characteristics = mol_characteristics.drop(['System'],axis=1)
    rt_file = Take_In_RT_Markers(rt_file)
    model = pickle.load(open(model_dir, "rb" ))
    rt_list = []
    col_A = Create_A_B_Columns(mol_characteristics,'A')
    col_B = Create_A_B_Columns(rt_file,'B')
    rt_file.columns = col_B
    mol_characteristics.columns = col_A
    rt_file.columns = col_B
    for index,row in rt_file.iterrows():
        rt = row['BRT']
        print(rt)
        rt_list.append(rt)
    mol_characteristics = mol_characteristics.reset_index()
    mol_characteristics = mol_characteristics.drop(['index'],axis=1)
    list_of_approved_cmpds = []
    list_of_unapproved_cmpds = []
    list_of_unsure_cmpds = []
    
#    test_list = []
    for index,row in mol_characteristics.iterrows():
        test_name = row['AName']
#        if test_name in metab_dict.keys():
#            test_list.append(test_name)
    #    print('On index {}'.format(index))
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
            list_of_unsure_cmpds.append([test_name,beginning_range,end_range,actual_rt])
        elif beginning_range < actual_rt < end_range and test_name not in list_of_approved_cmpds:
            list_of_approved_cmpds.append([test_name,beginning_range,end_range,actual_rt])
        elif not beginning_range < actual_rt < end_range and test_name not in list_of_unapproved_cmpds:
            list_of_unapproved_cmpds.append([test_name,beginning_range,end_range,actual_rt])
        print('Start range of RT is {} and end range of RT is {} for {}'.format(beginning_range,end_range,test_name))    
    total = len(list_of_approved_cmpds) + len(list_of_unapproved_cmpds) + len(list_of_unsure_cmpds)
    print('False positves removed {}, perventage is {}'.format(len(list_of_unapproved_cmpds),(len(list_of_unapproved_cmpds)/total) * 100))
    write_list_to_csv(list_of_approved_cmpds,file_dir + 'RT_Folder\\approved.csv')
    write_list_to_csv(list_of_unapproved_cmpds,file_dir + 'RT_Folder\\unapproved.csv')
    write_list_to_csv(list_of_unsure_cmpds,file_dir + 'RT_Folder\\unsure.csv')
    return list_of_approved_cmpds,list_of_unapproved_cmpds,list_of_unsure_cmpds
    
def One_Click_Program(file_dir,template_rt_file_dir,model_dir):
    startTime = datetime.now()
    mummichog_with_rts = Join_Mummichog_Results_Retention_Times(file_dir)
    print('To Process mummichog and unite them with Retention Times took {}'.format(datetime.now() - startTime))
    mummichog_with_rts_mol_features = Join_Mummichog_Matches_Molecular_Features(mummichog_with_rts,file_dir)
    print('To get all molecular features for the matches took {}'.format(datetime.now() - startTime))
    approved,unapproved,unsure = Run_Model_On_Punitive_Matches(mummichog_with_rts_mol_features,template_rt_file_dir,model_dir,file_dir)
    print('To run model took {}'.format(datetime.now() - startTime))
    
def xl_hello_world():
    wb = xw.Book('Interface.xlsm')
    sht = wb.sheets[0]
    sht.range('A1').value = 'hello_world'

def xl_one_click_program():
    wb0 = xw.Book('Interface.xlsm')
    sht0 = wb0.sheets[0]

    results_dir = sht0.range('B1').value
    temp_comps = sht0.range('B2').value
    model = sht0.range('B3').value

    One_Click_Program(results_dir,temp_comps,model)

if __name__ == '__main__':
    startTime = datetime.now()
    file_dir = 'C:\\Users\\rubya\\Desktop\\Forsberg Lab\\MainThesisFolderRTPred\\KristenResults\\results\\'
    template_rt_file_dir = r'C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\csvfiles\TemplateCompounds.csv'
    model_dir = r"C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\pickles\RFClassifier.pickle"
    One_Click_Program(file_dir,template_rt_file_dir,model_dir)
    print(datetime.now() - startTime)
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    