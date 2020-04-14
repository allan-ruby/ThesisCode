import pickle
import pandas as pd 


infile = open('SMRT_RAW_PICKLES_OUTPUT/compoundsupto1000_training_set.pickle','rb')

complete_DF= pickle.load(infile)
infile.close()

