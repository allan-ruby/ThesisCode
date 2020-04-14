import tkinter as tk 
from Retention_Confirmation_Workflow import One_Click_Program


    
    
    

Main_Window = tk.Tk()
Main_Window.title("Retention Verification Software")

folder_dir_lbl = tk.Label(Main_Window,text='Enter the file path to your xcms results')
folder_dir_lbl.grid(row=0,column=0)
folder_dir = tk.StringVar(Main_Window,value='C:\\Users\\rubya\\Desktop\\Forsberg Lab\\MainThesisFolderRTPred\\KristenResults\\results\\')
folder_dir_text_box = tk.Entry(Main_Window,textvariable=folder_dir)
folder_dir_text_box.grid(row=0,column=1)

ret_standards_dir_lbl = tk.Label(Main_Window,text='Enter the file path to the standard rt file')
ret_standards_dir_lbl.grid(row=1,column=0)
ret_standards_dir = tk.StringVar(Main_Window,value=r'C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\csvfiles\TemplateCompounds.csv')
ret_standards_text_box = tk.Entry(Main_Window,textvariable=ret_standards_dir)
ret_standards_text_box.grid(row=1,column=1)


model_dir_lbl = tk.Label(Main_Window,text='Enter the file path to the model to be used')
model_dir_lbl.grid(row=2,column=0)
model_dir = tk.StringVar(Main_Window,value=r"C:\Users\rubya\Desktop\Forsberg Lab\MainThesisFolderRTPred\pickles\RFClassifier.pickle")
model_dir_text_box = tk.Entry(Main_Window,textvariable=model_dir)
model_dir_text_box.grid(row=2,column=1)

def Begin_Processing():
    Processing_Button.config(relief=tk.SUNKEN,text='Processing')
    folder_dir_value = folder_dir.get()
    ret_standards_dir_value = ret_standards_dir.get()
    model_dir_value = model_dir.get()
    print(folder_dir_value + ret_standards_dir_value + model_dir_value)
    One_Click_Program(folder_dir_value,ret_standards_dir_value,model_dir_value)


Processing_Button = tk.Button(Main_Window,text = "Begin Processing",command = Begin_Processing)
Processing_Button.grid(row=3,column=0)



Main_Window.mainloop()




