import pickle
import pandas as pd


infile = open('output.p','rb')
complete_DF= pickle.load(infile)
system_dict = {}

for index,row in complete_DF.iterrows():
   if row['System'] not in system_dict.keys():
      system_dict[row['System']] = [index]
   else:
      value = system_dict[row['System']]
      value.append(index)
      system_dict[row['System']] = value
list_of_dataframes = []
for key in system_dict.keys():
	inter_df_list = []
	idx_list = system_dict[key]
	for index,row in complete_DF.iterrows():
		if index in idx_list:
			inter_df_list.append(row)
	inter_df = pd.DataFrame(inter_df_list)
	list_of_dataframes.append([key,inter_df])
col_A = []
col_B = []
for index,col in enumerate(complete_DF.columns):
	if index < 159:
	   col_A.append('A' + str(index))
	   col_B.append('B' + str(index))
	else:
		col_A.append('A' + col)
		col_B.append('B' + col)
###Creating a training set from FEM long
###FEM_long	412	Reversed-phase	Waters ACQUITY UPLC HSS T3 C18	acidic	Water:MeOH	0.1% FA	10.1007/s11306-011-0298-z
### C18 column, 50:50
for tup in list_of_dataframes:
	if tup[0] == 'FEM_long':
		df_fem_long = tup[1]
	if tup[0] == 'FEM_orbitrap_plasma':
		df_orb_plasma = tup[1]
#first_part = []
#second_part = []
def create_training_set(df_fem_long,output):
	df_list = []
	for i in range(len(df_fem_long)):
		print('On index {}'.format(i))
		first_part= df_fem_long.iloc[[i]]
		first_part.columns=col_A
		first_part = first_part.reset_index()
		for i2 in range(i+1,len(df_fem_long)):
	#		print(i2)
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
	#	print(row['ART'],row['BRT'])
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
#df_fem_long = create_training_set(df_fem_long,'fem_long.csv')
df_orb_plasma = create_training_set(df_orb_plasma,'FEM_orbitrap_plasma.csv')

print('output written')

