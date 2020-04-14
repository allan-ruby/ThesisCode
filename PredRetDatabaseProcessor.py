from rdkit import Chem, DataStructs
from rdkit.Chem.Fingerprints import FingerprintMols
from rdkit.Chem import MACCSkeys
import pubchempy as pcp
import pandas as pd
from rdkit.Chem.EState import Fingerprinter
import numpy as np
from rdkit.Chem import Descriptors
import pickle
#example testing: coing from inchi to testable features

def fps_plus_mw(mol):
    return np.append(Fingerprinter.FingerprintMol(mol),Descriptors.MolWt(mol))

def mol_prop_gen(dataframe,outputpickle):
#loading initial data
#    dataframe = pd.read_csv(filename)
#    newdf = pd.DataFrame()
    finaldf = pd.DataFrame()

    for index, row in dataframe.iterrows():
        
        if index == 0:
            name = row['Name']
            inchi = row['InChI']
            cmpd = pcp.get_compounds(inchi,'inchi')
            props = cmpd[0].to_dict(properties=['cactvs_fingerprint',
                        'isomeric_smiles', 'xlogp', 'rotatable_bond_count','charge','complexity',
                        'exact_mass','fingerprint'])
            smiles=props['isomeric_smiles']
            props['mol']=Chem.MolFromSmiles(smiles)
            props['RT'] = row['RT']
            props['Name'] = name
            props['System'] = row['System']
            desc = np.array(fps_plus_mw(props['mol']))
            descdf = pd.DataFrame(desc)
            descdf = descdf.T
            descdf.reindex([index])
            newdf=pd.DataFrame(props,index=[index])
            finaldf=pd.concat([descdf,newdf],axis=1)
            print('test')
        else:
            inchi = row['InChI']
        try:
            cmpd = pcp.get_compounds(inchi,'inchi')
        except:
            print('line bypassed')
            pass
        try:
            props = cmpd[0].to_dict(properties=['cactvs_fingerprint','isomeric_smiles', 'xlogp', 'rotatable_bond_count','charge','complexity','exact_mass','fingerprint'])
        except:
            print('line bypassed')
            pass
        name = row['Name']
        smiles=props['isomeric_smiles']
        props['mol']=Chem.MolFromSmiles(smiles)
        props['RT'] = row['RT']
        props['Name'] = name
        props['System'] = row['System']
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
        print('on index ' + str(index+1) + ' of ' + str(len(dataframe)))
        finaldf.to_pickle(outputpickle)


#mol_prop_gen('PredRetDB.csv','test.pickle')