import pickle
import pandas as pd
import os
def create_training_set(df_fem_long,output):
    col_A= []
    col_B = []
    for index,col in enumerate(df_fem_long.columns):
      if index < 159:
         col_A.append('A' + str(index))
         col_B.append('B' + str(index))
      else:
           col_A.append('A' + col)
           col_B.append('B' + col)
    df_list = []
    for i in range(len(df_fem_long)):
#    for i in range(10): for testing
        print('On index {}'.format(i + 1))
        first_part= df_fem_long.iloc[[i]]
        first_part.columns=col_A
        first_part = first_part.reset_index()
        for i2 in range(i+1,len(df_fem_long)):
#        for i2 in range(i+1,10): for testing
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

    train_df.to_pickle(output)
    print('output written')
    return train_df

#infile = open('compoundsupto1000.pickle','rb')
#df = pickle.load(infile)
##df.rename(columns={158:'RT'},inplace=True)
#infile.close()
#df = create_training_set(df,'compoundsupto1000_training_set.pickle')
for file in os.listdir('SMRT_RAW_PICKLES/'):
    print(file)
    infile = open('SMRT_RAW_PICKLES/' + file, 'rb')
    df = pickle.load(infile)
#    df.rename(columns={158:'RT'},inplace=True)
    infile.close()
    df = create_training_set(df, 'SMRT_RAW_PICKLES_OUTPUT/' + file[0:-7] + 'training_set.p')
    print(file + ' is done and output is written')
    os.rename('SMRT_RAW_PICKLES/' + file, 'SMRT_PROCESSED/' + file)
    print('finished file name {}'.format(file))
    