'''
The GUI_Console is the GUI for entering queries, showing results and displaying graphs
The Graph Panel is still in developing. Currently, the GUI just show an example in the Graph Panel

If press enter and the last char is ";", then end the query input,
If press F1, clear text and continue for next query

@author: minjianliu
'''
from Tkinter import * #GUI package
from PIL import Image, ImageTk #for Tkinter to support png figure
import queryConsole
#import Image, ImageTk

#Key event for Query Text
def query_Text_Event(event):        
    #if press enter and the last char is ";", then end the query input,     
    if event.keycode == 36: 
        query = query_Text.get(1.0, END).strip()
        if query[-1] == ";":
            queryConsole.start(query, result_Text)
            query_Text.config(state=DISABLED)
    
    #press F1, clear text and continue for next query
    if event.keycode == 67:
        query_Text.config(state=NORMAL)
        query_Text.delete("1.0", END)
        result_Text.config(state=NORMAL)
        result_Text.delete("1.0", END)
        result_Text.config(state=DISABLED)

#the root window
root = Tk() 
root.title("RG Framework Console")
root.resizable(False, False)

#panel for query enter
query_Frame = LabelFrame(root, text="Query Panel")
query_Frame.grid(row=0, column=0, padx=5, pady=5)

#panel for showing results 
result_Frame = LabelFrame(root, text="Result Panel")
result_Frame.grid(row=1, column=0, padx=5, pady=5)

#panel for showing graphs
graph_Frame = LabelFrame(root, text="Graph Panel", height=460, width=300)
graph_Frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5)

#Scroll bars in the query panel 
sbx_for_query = Scrollbar(query_Frame, orient=HORIZONTAL)
sbx_for_query.grid(row=1, column=0, sticky=W+E)
sby_for_query = Scrollbar(query_Frame)
sby_for_query.grid(row=0, column=1, sticky=N+S)

#Scroll bars in the result panel
sbx_for_result = Scrollbar(result_Frame, orient=HORIZONTAL)
sbx_for_result.grid(row=1, column=0, sticky=W+E)
sby_for_result = Scrollbar(result_Frame)
sby_for_result.grid(row=0, column=1, sticky=N+S)


#Text widget for query panel
query_Text = Text(query_Frame, width=70, height=10, wrap=NONE, xscrollcommand=sbx_for_query.set, yscrollcommand=sby_for_query.set)
sbx_for_query.config(command=query_Text.xview)
sby_for_query.config(command=query_Text.yview)
query_Text.grid(row=0, column=0)
        
query_Text.bind('<Key>', query_Text_Event)

#Text widget for result panel
result_Text = Text(result_Frame, width=70, height=15, wrap=NONE, xscrollcommand=sbx_for_result.set, yscrollcommand=sby_for_result.set)
result_Text.config(state=DISABLED)
sbx_for_result.config(command=result_Text.xview)
sby_for_result.config(command=result_Text.yview)
result_Text.grid(row=0, column=0)

#showing graph images
image = Image.open("coauthorship_topk.png")
photo = ImageTk.PhotoImage(image)
imgLabel = Label(graph_Frame, image=photo)
imgLabel.place(relx=0.5, rely=0.5, anchor=CENTER)

mainloop()
