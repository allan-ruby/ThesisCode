import pandas as pd
import pubchempy as pcp


filedir = 'C:\\Users\\rubya\\Desktop\\Forsberg Lab\\MainThesisFolderRTPred\\KristenResults\\results\\'


results = pd.read_csv(filedir + 'results.tsv',sep='\t',encoding = "ISO-8859-1")
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
    print('on index {} of {}'.format(index+1,len(id_df)))
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

final_df.to_csv('mummichog_results_with_retention_times.csv')

