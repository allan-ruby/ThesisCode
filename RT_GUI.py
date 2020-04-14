import tkinter as tk


class Window1():
    def __init__(self,parent,*args,**kwargs):
        self.parent = parent
        instructions = """
        Please put the directory to your XCMS results folder.
        Export the results table and save it as "results.csv"
        in "yourxcmxfolder/results/results.csv" format
        """
        self.parent.title('Retention Time Prediction')
        directions =tk.Label(self.parent,text=instructions)
        directions.grid(row=0,column=0)
        label = tk.Label(self.parent, text='Specify your XCMS directory')
        label.grid(row=1,column=0)
        
        e1 = tk.Entry(self.parent)
        e1.grid(row=2,column=0)
        
        model_variable = tk.StringVar(self.parent)
        model_variable.set('Choose Model')
        fake_model_names = ['Random Forest','Nueral Network']
        dropdown = tk.OptionMenu(self.parent,model_variable,*fake_model_names)
        dropdown.grid(row=3,column=0)
        
        self.process_button = tk.Button(self.parent,text = 'Process', command = self.test_press)
        self.process_button.grid(row=4,column=0)
        
        self.train_model_button = tk.Button(self.parent,text = 'Train New Model', command = self.test_press2)
        self.train_model_button.grid(row=5,column=0)

        
    def test_press(self):
        self.process_button.destroy()
        new_label = tk.Label(self.parent,text = 'Processed')
        new_label.grid(row=4,column=0)
        
    def test_press2(self):
        self.train_model_button.destroy()
        new_label2 = tk.Label(self.parent,text = 'Mode not yet created')
        new_label2.grid(row=5,column=0)
        
        









if __name__ == '__main__':
    root = tk.Tk()
    Window1(root)
    root.mainloop()

