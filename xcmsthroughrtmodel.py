import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem.Fingerprints import FingerprintMols
from rdkit.Chem import MACCSkeys
import pubchempy as pcp
import pandas as pd
from rdkit.Chem.EState import Fingerprinter
import numpy as np
from rdkit.Chem import Descriptors
import pickle
from PredRetDatabaseProcessor import fps_plus_mw

result_df = pd.read_csv('mummichog_results_with_retention_times.csv')
result_df = result_df.drop(['Unnamed: 0'], axis=1)
running_cmpd_list = []
for index,row in result_df.iterrows():
#    print(row['Compound Name'],row['rtmin'],row['rtmax'])
    
    if index == 0:
        name = row['Compound Name']
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
finaldf.to_pickle('mummichog_rt_features.p')