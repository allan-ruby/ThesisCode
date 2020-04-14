import pandas as pd
from PredRetDatabaseProcessor import mol_prop_gen, fps_plus_mw
from rdkit import Chem, DataStructs
from rdkit.Chem.Fingerprints import FingerprintMols
from rdkit.Chem import MACCSkeys
import pubchempy as pcp
from rdkit.Chem.EState import Fingerprinter
import numpy as np
from rdkit.Chem import Descriptors
import pickle

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

def Take_In_Test_Cmpds(file):
    df = pd.read_csv(file)
    list_data_df = []
    for index,row in df.iterrows():
        name = row[0]
        inchi = row[1]
        list_data_df.append(generate_data(name,inchi))
    return pd.concat(list_data_df)
def Create_A_B_Columns(complete_DF):
    col_A = []
    col_B = []
    for index,col in enumerate(complete_DF.columns):
        if index < 159:
           col_A.append('A' + str(index))
           col_B.append('B' + str(index))
        else:
            col_A.append('A' + col)
            col_B.append('B' + col)
    return col_A, col_B


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
    train_df =train_df.drop(['ART','BRT','AName','BName','index','Amol','Bmol','Aisomeric_smiles','Bisomeric_smiles','ASystem','BSystem','Afingerprint','Bfingerprint','Acactvs_fingerprint','Bcactvs_fingerprint'],axis=1)
    train_df = train_df.fillna(0)

    train_df.to_csv(output)
    return train_df


rt_list = []
final_df = Take_In_RT_Markers(r'C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\csvfiles\TemplateCompounds.csv')
col_A, col_B = Create_A_B_Columns(final_df) 
final_df.columns = col_B
for index,row in final_df.iterrows():
    rt = row['BRT']
    print(rt)
    rt_list.append(rt)
test_cmpd = Take_In_Test_Cmpds(r'C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\csvfiles\compound_of_interest.csv')
test_cmpd.columns = col_A
test_name = test_cmpd['AName'][0]
df_list = []
for i in range(len(final_df)):
    entry = []
    entry = [test_cmpd.iloc[[0]].reset_index(),final_df.iloc[[i]].reset_index()]
    df = pd.concat(entry,axis=1)
    df_list.append(df)
essential_df = pd.concat(df_list,ignore_index=True)
essential_df = essential_df.drop(['ART','BRT','AName','BName','index','Amol','Bmol','Aisomeric_smiles','Bisomeric_smiles','ASystem','BSystem','Afingerprint','Bfingerprint','Acactvs_fingerprint','Bcactvs_fingerprint'],axis=1)

model = pickle.load(open(r"C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\pickles\RFClassifier.pickle", "rb" ))
predictions = list(model.predict(essential_df))
prob_A = list(model.predict_proba(essential_df))
end_range = 100.0
beginning_range = 0.00
for index,result in enumerate(predictions):
    rt = rt_list[index]
    if prob_A[index][0] > .45 and prob_A[index][0] < .55:
        break
    if result == 1 and rt < end_range:
        end_range = rt
    if result == 0 and rt > beginning_range:
        beginning_range = rt
print('Start range of RT is {} and end range of RT is {} for {}'.format(beginning_range,end_range,test_name))
        
        
#RT_status = []
#for index,row in essential_df.iterrows():
#    if type(row['ART']) == str:
#        a_RT = float(row['ART'])
#    b_RT = float(row['BRT'])
#    if a_RT == b_RT:
#        RT_status.append('error')
#    elif a_RT > b_RT:
#        RT_status.append(0)
#    elif b_RT > a_RT:
#        RT_status.append(1)
#    else:
#        RT_status.append('error')
#essential_df['Result'] = RT_status
