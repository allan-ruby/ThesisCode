import pandas as pd
from PredRetDatabaseProcessor import fps_plus_mw, mol_prop_gen

Pred_Ret_DF = pd.read_csv('PredRetDB.csv')

phase_type_df = pd.read_csv('PredRetsystemtocoltype.csv')

col_parameters = pd.read_csv('column_parameters.csv')
col_dict = {}

for indx,row in col_parameters.iterrows():
	if row[3] not in col_dict:
		col_dict[row[3]] = [row[0]]
	else:
		value = col_dict[row[3]]
		value.append(row[0])
		col_dict[row[3]] = value
system_dict = {}
for indx,row in col_parameters.iterrows():
	system_dict[row[0]] = row[3]
df_list = []	
for indx,row in Pred_Ret_DF.iterrows():
	try:
		col = system_dict[row[2]]
	except:
		break
	if col == 'Waters ACQUITY UPLC HSS T3 C18':
		df_list.append(row)

c18HSST3_resuts = pd.DataFrame(df_list)
mol_prop_gen(c18HSST3_resuts,'output.p')
		