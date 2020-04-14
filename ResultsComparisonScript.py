import pandas as pd
import numpy as np

def take_in_important_metabolites_file(file_name):
    list_of_metabolite_names = []
    with open(file_name) as file:
        for line in file.readlines():
            line = line.strip().split(',')
            if len(line[0]) > 0:
                list_of_metabolite_names.append(line[1])
    return list_of_metabolite_names


def take_in_results(file):
    df = pd.read_csv(file)
    return pd.Series(row[1] for index,row in df.iterrows())



imp_metabs_df = pd.Series(take_in_important_metabolites_file('top_metabolites_predictions_jobid_1376400.csv'))
df_approved = take_in_results('approved.csv')
df_unapproved = take_in_results('unapproved.csv')
df_unsure = take_in_results('unsure.csv')

approved = pd.Series(np.intersect1d(df_approved.values,imp_metabs_df.values))
unapproved = pd.Series(np.intersect1d(df_unapproved.values,imp_metabs_df.values))
unsure = pd.Series(np.intersect1d(df_unsure.values,imp_metabs_df.values))



