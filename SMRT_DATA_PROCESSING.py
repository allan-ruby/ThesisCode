import sdf
import pubchempy as pcp
from PredRetDatabaseProcessor import fps_plus_mw
from rdkit import Chem, DataStructs
import numpy as np
import pandas as pd
import time
import pickle
#data = sdf.load('8038913/SMRT_dataset.sdf','/v', unit='V', scale_units=['s'])

#tree = ET.parse('8038913/SMRT_dataset.sdf')
#for root in tree:
#    print(root.tag)
cid_dict = {}
with open('8038913/SMRT_dataset.sdf','r') as f:
    state = ''
    num = 1
    for line in f.readlines():
        if state == 'Log CID':
            key = line
            state = 'Wait for RT Time'
        if state == 'Log RT':
            cid_dict[key] = float(line)
            state = ''
            print('On Compound {}'.format(str(num)))
            num +=1
        if line.startswith('> <PUBCHEM_COMPOUND_CID>'):
            state = 'Log CID'
        if line.startswith('> <RETENTION_TIME>'):
            state = 'Log RT'
num = 1
saving_count = 1
list_of_df = []
list_of_unprocessed = []
list_of_processed = []
for cid in cid_dict.keys():
    
    print('On compound {}'.format(num))
    try:
        cmpd = pcp.get_compounds(cid,'cid')
        list_of_processed.append(cid)
    except:
        list_of_unprocessed.append(cid)
        time.sleep(10)
        pd.DataFrame(list_of_unprocessed).to_pickle('compounds_skipped.pickle')
#    props = cmpd[0].to_dict(properties=['cactvs_fingerprint',
#                        'isomeric_smiles', 'xlogp', 'rotatable_bond_count','charge','complexity',
#                        'exact_mass','fingerprint'])
    name = cmpd[0].iupac_name
    rt = cid_dict[cid]
    props = cmpd[0].to_dict(properties=['cactvs_fingerprint',
                        'isomeric_smiles', 'xlogp', 'rotatable_bond_count','charge','complexity',
                        'exact_mass','fingerprint'])
    smiles=props['isomeric_smiles']
    props['mol']=Chem.MolFromSmiles(smiles)
    props['Name'] = name
    props['System'] = 'SMRT DATA'
    props['RT'] = rt
    desc = np.array(fps_plus_mw(props['mol']))
    descdf = pd.DataFrame(desc)
    descdf = descdf.T
    descdf.reindex([num])
    newdf=pd.DataFrame(props,index=[0])
    finaldf=pd.concat([descdf,newdf],axis=1)
    list_of_df.append(finaldf)
    num +=1
    saving_count += 1
    if saving_count > 999:
        final_df = pd.concat(list_of_df)
        final_df.to_pickle('compoundsupto' + str(num) + '.pickle')
        saving_count = 1
        list_of_df = []
        with open('processed.p', 'wb') as f:
            pickle.dump(list_of_processed,f)
    
pd.DataFrame(list_of_unprocessed).to_pickle('compounds_skipped.pickle')        
#    props = cmpd[0].to_dict(properties=['iupac_name'])
    
    
    