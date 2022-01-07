import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
#from PIL import ImageTk, Image
from tkinter import filedialog
import os
from tkinter import messagebox
from tkinter import *

import PIL.Image
import PIL.ImageTk
from PIL import ImageGrab

from os import path
import math
import time

import shapely
from shapely.geometry import LineString, Point

class GridWindow:
    def __init__(self, parent, status):
        self.status = status
        self.myParent = parent
        self.myContainer1 = tk.Frame(parent)
        self.myContainer1.pack()
        self.cellwidth = 40
        self.cellheight = 40
        self.rect = {}
        self.GRID = 3
        self.mode = ''
        self.str_GT = ''
        self.str_gen_Detial = ''
        self.line_intersection = []
        self.sub_line_intersection = []
        self.status_remove = False
        self.Matrix_grid = np.zeros((20, 20), dtype=int)
        self.Matrix_id_line = np.zeros((20, 20), dtype=int)
        self.Matrix_order_node = np.zeros((20, 20), dtype=int)
        self.Matrix_x = np.zeros((20, 20), dtype=float)
        self.Matrix_y = np.zeros((20, 20), dtype=float)
        self.Clicked = False
        self.num_gen = 0
        self.line_position = []
        self.mode = ''
        self.generator_dict = {}
        self.counter = 0
        self.counter_text = 0
        self.gen_column = []
        self.twist_status = False

        self.menubar = Menu(mainWindow)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Calculate", command=lambda: self.calculate())
        self.filemenu.add_command(label="Add connection", command=lambda: self.connecting())
        self.filemenu.add_command(label="Graph -> text (export result -> .txt)", command=lambda: self.Export())
        self.filemenu.add_command(label="Text -> graph (export graph -> .jpg)", command=lambda: self.Export())
        self.filemenu.add_command(label="Remove generator or id", command=lambda: self.Remove())
        self.filemenu.add_command(label="Check error", command=lambda: self.Check_error())
        #self.filemenu.add_command(label="Twist", command=lambda: self.twist())
        self.filemenu.add_command(label="Reset graph (graph -> text)", command=lambda: self.reset_graph_GT_clear_table())
        self.filemenu.add_command(label="Reset graph (text -> graph)", command=lambda: self.reset_graph_TG_clear_table())
        self.filemenu.add_command(label="Clear objects (text -> graph)", command=lambda: self.reset_graph_TG_remove_file())
        self.filemenu.add_command(label="Cursor", command=self.cursor)
        self.filemenu.add_separator()

        self.filemenu.add_command(label="Exit", command=self.myParent.quit)

        #self.filemenu.bind('<<MenuSelect>>', self.menucallback)

        self.menubar.add_cascade(label="Action", menu=self.filemenu)
        mainWindow.config(menu=self.menubar)

        self.menucallback()

    def reset_graph_TG_remove_file(self):
        MsgBox = tk.messagebox.askquestion('delete', 'Delete old generator ?', icon='warning')
        if MsgBox == 'yes':
            os.remove('generator_info.txt')

    def reset_graph_TG_clear_table(self):
        self.myContainer1.destroy()
        self.myContainer1 = tk.Frame(self.myParent)
        self.myContainer1.pack()
        self.draw_grid(20, 20)
        self.myCanvas.update()

        self.Matrix_grid = np.zeros((20, 20), dtype=int)
        self.Matrix_id_line = np.zeros((20, 20), dtype=int)
        self.Matrix_order_node = np.zeros((20, 20), dtype=int)
        self.Clicked = False
        self.num_gen = 0
        self.line_position = []
        self.mode = ''
        self.generator_dict = {}
        self.counter = 0
        self.counter_text = 0
        self.gen_column = []

    def reset_graph_GT_clear_table(self):
        self.myContainer1.destroy()
        self.myContainer1 = tk.Frame(self.myParent)
        self.myContainer1.pack()
        self.draw_grid(20, 20)
        self.myCanvas.update()

        self.Matrix_grid = np.zeros((20, 20), dtype=int)
        self.Matrix_id_line = np.zeros((20, 20), dtype=int)
        self.Matrix_order_node = np.zeros((20, 20), dtype=int)
        self.Clicked = False
        self.num_gen = 0
        self.line_position = []
        self.mode = ''
        self.generator_dict = {}
        self.counter = 0
        self.counter_text = 0
        self.gen_column = []

    def menucallback(self):
        global draw_tab_1, draw_tab_2

        if draw_tab_1 == True and draw_tab_2 == False:
            self.filemenu.entryconfig(2, state=tk.DISABLED)
            self.filemenu.entryconfig(3, state=tk.NORMAL)

            self.filemenu.entryconfig(6, state=tk.DISABLED)
            self.filemenu.entryconfig(7, state=tk.NORMAL)
            self.filemenu.entryconfig(8, state=tk.NORMAL)

        elif draw_tab_2 == True and draw_tab_1 == False:
            self.filemenu.entryconfig(2, state=tk.NORMAL)
            self.filemenu.entryconfig(3, state=tk.DISABLED)

            self.filemenu.entryconfig(6, state=tk.NORMAL)
            self.filemenu.entryconfig(7, state=tk.DISABLED)
            self.filemenu.entryconfig(8, state=tk.DISABLED)
        else:
            self.filemenu.entryconfig(2, state=tk.NORMAL)
            self.filemenu.entryconfig(3, state=tk.DISABLED)

            self.filemenu.entryconfig(6, state=tk.NORMAL)
            self.filemenu.entryconfig(7, state=tk.DISABLED)
            self.filemenu.entryconfig(8, state=tk.DISABLED)


    def check_intersection_line(self, point_line1_1, point_line1_2, point_line2_1, point_line2_2):
        point_of_intersection = []
        try:

            line1 = LineString([point_line1_1, point_line1_2])
            line2 = LineString([point_line2_1, point_line2_2])

            int_pt = line1.intersection(line2)
            point_of_intersection = int_pt.x, int_pt.y

        except Exception as ex:

            point_of_intersection = []

        return point_of_intersection

    def Check_error(self):
        [r, c] = self.Matrix_grid.shape
        for j in range(r - 1):
            for i in range(c - 1):
                if self.Matrix_grid[j, i] == -1:
                    count1 = 0
                    if self.Matrix_grid[j - 1, i] == -1:
                        count1 += 1
                    if self.Matrix_grid[j + 1, i] == -1:
                        count1 += 1
                    if self.Matrix_grid[j, i - 1] == -1:
                        count1 += 1
                    if self.Matrix_grid[j, i + 1] == -1:
                        count1 += 1

                    if count1 <= 1:
                        messagebox.showinfo("Check error", "Error row : " + str(j + 1) + "col : " + str(i + 1))

                elif self.Matrix_grid[j, i] > -1:
                    count2 = 0
                    if self.Matrix_grid[j, i + 1] > 0 and self.Matrix_grid[j, i - 1] > 0 and self.Matrix_grid[j - 1, i] == 0 and self.Matrix_grid[j + 1, i] == 0:
                        messagebox.showinfo("Check error", "Error row : " + str(j + 1) + "col : " + str(i + 1))

    def Remove(self):
        self.status_remove = True
        self.mode = ''

    def Export(self):
        global draw_tab_1, draw_tab_2

        '''
        #print('draw_tab_1 : {}'.format(draw_tab_1))
        #print('draw_tab_2 : {}'.format(draw_tab_2))
        if draw_tab_1 == True and draw_tab_2 == False:

            self.status_export = 'GT'
            self.str_GT = '('
            [r, c] = self.Matrix_grid.shape
            for i in range(r):
                if sum(self.Matrix_grid[:, i]) > 0:
                    duplicated = -100
                    for j in range(c):
                        if self.Matrix_grid[j, i] > 0 and self.Matrix_grid[j, i] != duplicated:
                            with open("create_gt.txt", 'r') as file_in:
                                for line in file_in:
                                    str = line.split(',')
                                    column = int(str[0])
                                    num_gen = int(str[1])
                                    x = int(str[2])
                                    y = int(str[3])
                                    input = int(str[4])
                                    output = int(str[5])
                                    gen_color = str[6]
                                    name = str[7].replace('\n', '')

                                    duplicated = num_gen

                                    if self.Matrix_grid[j, i] == num_gen:
                                        self.str_GT += name + ';'
                                        break
                        elif self.Matrix_grid[j, i] == -1:
                                self.str_GT += 'id;'
                    self.str_GT += ');('

            '''

        if draw_tab_1 == True and draw_tab_2 == False:

            self.status_export = 'GT'
            M = self.get_Matrix_grid()

            c = 0
            tmp = ''
            log = 0
            [row, col] = M.shape
            self.gen_column = list(dict.fromkeys(self.gen_column))
            self.gen_column = sorted(self.gen_column)
            for i in range(len(self.gen_column)):
                tmp += '('
                log = ''
                for j in range(row):
                    if M[j, self.gen_column[i] - 1] == -1:
                        tmp += 'id * '
                    elif M[j, self.gen_column[i] - 1] == -2 and M[j, self.gen_column[i] - 1] != log:
                        log = M[j, self.gen_column[i] - 1]
                        tmp += 'twist * '
                    elif M[j, self.gen_column[i] - 1] != 0 and M[j, self.gen_column[i] - 1] != log:
                        log = M[j, self.gen_column[i] - 1]
                        tmp += str(self.generator_dict.get(M[j, self.gen_column[i] - 1])) + ' * '
                tmp = tmp[:-3]
                tmp += ') ; '

                '''
                # check count
                count = tmp.count(';')
                if count <= 1:
                    tmp = tmp.replace(';', '')
                '''

                tmp = tmp.strip()[:-1]
                if len(tmp) < 4:
                    with open('graph_to_text_export.txt', 'w') as f:
                        f.write(tmp)

            messagebox.showinfo("Export", "Graph to text export completed !")

        elif draw_tab_2 == True and draw_tab_1 == False:

            self.status_export = 'TG'

            time.sleep(1)
            x = self.myParent.winfo_rootx()
            y = self.myParent.winfo_rooty()
            height = self.myParent.winfo_height() + y
            width = self.myParent.winfo_width() + x
            ImageGrab.grab().crop((x, y, width, height)).save('Text_to_graph.jpg')

            messagebox.showinfo("Export", "Text to graph export completed !")

    def set_mode(self, m):
        self.mode = m

    def set_num_gen(self, g):
        self.num_gen = g

    def get_Matrix_grid(self):
        return self.Matrix_grid

    def draw_grid(self, rows, columns):

        self.myCanvas = tk.Canvas(self.myContainer1)
        self.myCanvas.configure(width=self.cellheight*rows+4, height=self.cellwidth*columns+4)
        self.myCanvas.pack(side=tk.RIGHT)

        for column in range(rows):
            for row in range(columns):
                x1 = column * self.cellwidth+4
                y1 = row * self.cellheight+4
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.rect[row, column] = self.myCanvas.create_rectangle(x1, y1, x2, y2, fill="white")
                self.Matrix_x[row, column] = x2
                self.Matrix_y[row, column] = y2

        self.myCanvas.bind('<Motion>', self.mot)
        self.myCanvas.bind("<Button 1>", self.getorigin)
        self.myCanvas.bind("<Button 3>", self.click_right_button)

        ov = self.myCanvas.create_oval(-3, -3, 3, 3, tags='point', fill='red')

        #self.myCanvas.mainloop()

    def __del__(self):
        print('Destructor !')

    def On_clicked(self, e):
        if self.mode == 'connecting' and self.Clicked == False:
            self.Clicked = True
        elif self.mode == 'connecting' and self.Clicked == True:
            self.Clicked = False
        print('Click canvas !')

    def mot(self, e):
        #print(self.Clicked)
        xg = (e.x + self.GRID / 2) // self.GRID
        yg = (e.y + self.GRID / 2) // self.GRID
        t = self.myCanvas.find_withtag('point')
        #print('in Class : {}'.format(self.mode))
        if self.mode == 'connecting' and self.Clicked:
            column = e.x // (40)
            row = e.y // (40)

            if self.Matrix_grid[row, column] == 0:
                self.Matrix_grid[row, column] = -1
            print(self.Matrix_grid)

            row += 1
            column += 1
            print("Move ", (xg, yg), "Grid coordinates: ", row, column)

        self.set_oval_coords(t, (xg * self.GRID, yg * self.GRID))
        #print("self.Clicked : {}".format(self.Clicked))

    def set_oval_coords(self, t, xy):
        x, y = xy
        self.myCanvas.coords(t, (x - 5, y - 5, x + 5, y + 5))

    def draw_line_id(self, txt):

        # Mark id
        r = 0
        c = 0
        [rows, cols] = self.Matrix_grid.shape

        #txt = self.T.get().strip() # read input text
        Semi_colon = txt.split(';') # split input text

        # Mark id
        for i in range(len(Semi_colon)):
            Sub_semi_colon = Semi_colon[i]
            Star = Sub_semi_colon.split('*')
            for j in range(len(Star)):
                Sub_star = Star[j].replace('(', '').replace(')', '').strip()
                if Sub_star == 'id':
                    self.Matrix_grid[r, c] = -9
                    #print(self.Matrix_grid)
                    r += 1
                else: # is generator
                    r = 0
                    for m in range(rows):
                        if self.Matrix_grid[m, c] > 0:
                            break
                        else:
                            r += 1
                    r += 3
            c += 2
            r = 0

        # Order node
        for i in range(cols):
            ns = 0
            count = 0
            replace_count = 0
            for j in range(rows):
                v = self.Matrix_grid[j, i]
                if v != 0 and v != ns:
                    ns = v
                    count += 1
                    self.Matrix_id_line[j, i] = count
                    ns = self.Matrix_grid[j, i]
                    #print(self.Matrix_id_line)
                elif v != 0 and v == ns and v != -9:
                    ns = v
                    replace_count += 1
                    if replace_count >= 2:
                        replace_count = 0
                        count += 1
                        self.Matrix_id_line[j, i] = count
                        #print(self.Matrix_id_line)
                    else:
                        self.Matrix_id_line[j, i] = -7
                elif v != 0 and v == ns and v == -9:
                    ns = v
                    replace_count += 1
                    if replace_count > 0:
                        replace_count = 0
                        count += 1
                        self.Matrix_id_line[j, i] = count

        print(self.Matrix_id_line)

    def draw_generator_of_remove(self, x, y, input, output, gen_color, Name):

        self.create_circle(x + 6, y - 11, 10, gen_color)

        column = x // (40)
        row = y // (40)

        #self.str_GT = str(column) + ',' + str(self.num_gen) + ',' + str(x) + ',' + str(y) + ',' + str(
         #   input) + ',' + str(output) + ',' + gen_color + ',' + Name + '\n'
        #with open('create_gt.txt', 'a+') as f:
         #   f.write(self.str_GT)

        '''
        self.Matrix_grid[row, column] = self.num_gen
        self.Matrix_grid[row + 1, column] = self.num_gen
        self.Matrix_grid[row - 1, column] = self.num_gen
        print(self.Matrix_grid)
        '''

        row += 1
        column += 1

        # print('Create gen {} , {}'.format(row, column))

        # output
        str_tmp = ''
        # p_output_x = str(x + 17)
        # p_output_y = str(y - 10)
        if output % 2 == 0:
            for i in range(int(output / 2)):
                self.draw_line(x + 26, y - (50 + (i * 40)), x + 17, y - 10)
                self.draw_line(x + 26, y + (30 + (i * 40)), x + 17, y - 10)
                str_tmp += 'output,' + str(x + 26) + ',' + str(y - (50 + (i * 40))) + '\n'
                str_tmp += 'output,' + str(x + 26) + ',' + str(y + (30 + (i * 40))) + '\n'
        else:
            self.draw_line(x + 26, y - 10, x + 17, y - 10)
            str_tmp += 'output,' + str(x + 26) + ',' + str(y - 10) + '\n'
            for i in range(int(output / 2)):
                self.draw_line(x + 26, y - (50 + (i * 40)), x + 17, y - 10)
                self.draw_line(x + 26, y + (35 + (i * 40)), x + 17, y - 10)
                str_tmp += 'output,' + str(x + 26) + ',' + str(y - (50 + (i * 40))) + '\n'
                str_tmp += 'output,' + str(x + 26) + ',' + str(y + (35 + (i * 40))) + '\n'

        # input
        # p_input_x = str(x - 4)
        # p_input_y = str(y - 10)
        if input % 2 == 0:
            for i in range(int(input / 2)):
                self.draw_line(x - 13, y - (50 + (i * 40)), x - 4, y - 10)
                self.draw_line(x - 13, y + (30 + (i * 40)), x - 4, y - 10)
                str_tmp += 'input,' + str(x - 13) + ',' + str(y - (50 + (i * 40))) + '\n'
                str_tmp += 'input,' + str(x - 13) + ',' + str(y + (30 + (i * 40))) + '\n'
        else:
            self.draw_line(x - 13, y - 10, x - 4, y - 10)
            str_tmp += 'input,' + str(x - 13) + ',' + str(y - 10) + '\n'
            for i in range(int(input / 2)):
                self.draw_line(x - 13, y - (50 + (i * 40)), x - 4, y - 10)
                self.draw_line(x - 13, y + (35 + (i * 40)), x - 4, y - 10)
                str_tmp += 'input,' + str(x - 13) + ',' + str(y - (50 + (i * 40))) + '\n'
                str_tmp += 'input,' + str(x - 13) + ',' + str(y + (35 + (i * 40))) + '\n'

        #with open('gen.txt', 'a+') as f:
            #f.write(str_tmp)

    def draw_generator_TG(self, x, y, input, output, gen_color, Name):

        self.create_circle(x + 6, y - 11, 10, gen_color)

        column = x // (40)
        row = y // (40)

        self.Matrix_grid[row, column] = self.num_gen
        self.Matrix_grid[row + 1, column] = self.num_gen
        self.Matrix_grid[row - 1, column] = self.num_gen
        print(self.Matrix_grid)

        row += 1
        column += 1

        # print('Create gen {} , {}'.format(row, column))

        # output
        str_tmp = Name + '|'
        # p_output_x = str(x + 17)
        # p_output_y = str(y - 10)
        if output % 2 == 0:
            for i in range(int(output / 2)):
                self.draw_line(x + 26, y - (50 + (i * 40)), x + 17, y - 10)
                self.draw_line(x + 26, y + (30 + (i * 40)), x + 17, y - 10)
                str_tmp += 'output=' + str(x + 26) + ',' + str(y - (50 + (i * 40))) + '|'
                str_tmp += 'output=' + str(x + 26) + ',' + str(y + (30 + (i * 40))) + '|'
        else:
            self.draw_line(x + 26, y - 10, x + 17, y - 10)
            str_tmp += 'output=' + str(x + 26) + ',' + str(y - 10) + '|'
            for i in range(int(output / 2)):
                self.draw_line(x + 26, y - (50 + (i * 40)), x + 17, y - 10)
                self.draw_line(x + 26, y + (35 + (i * 40)), x + 17, y - 10)
                str_tmp += 'output=' + str(x + 26) + ',' + str(y - (50 + (i * 40))) + '|'
                str_tmp += 'output=' + str(x + 26) + ',' + str(y + (35 + (i * 40))) + '|'

        # input
        # p_input_x = str(x - 4)
        # p_input_y = str(y - 10)
        if input % 2 == 0:
            for i in range(int(input / 2)):
                self.draw_line(x - 13, y - (50 + (i * 40)), x - 4, y - 10)
                self.draw_line(x - 13, y + (30 + (i * 40)), x - 4, y - 10)
                str_tmp += 'input=' + str(x - 13) + ',' + str(y - (50 + (i * 40))) + '|'
                str_tmp += 'input=' + str(x - 13) + ',' + str(y + (30 + (i * 40))) + '|'
        else:
            self.draw_line(x - 13, y - 10, x - 4, y - 10)
            str_tmp += 'input=' + str(x - 13) + ',' + str(y - 10) + '|'
            for i in range(int(input / 2)):
                self.draw_line(x - 13, y - (50 + (i * 40)), x - 4, y - 10)
                self.draw_line(x - 13, y + (35 + (i * 40)), x - 4, y - 10)
                str_tmp += 'input=' + str(x - 13) + ',' + str(y - (50 + (i * 40))) + '|'
                str_tmp += 'input=' + str(x - 13) + ',' + str(y + (35 + (i * 40))) + '|'

        str_tmp += "\n"

        with open('gen_input_output_detial.txt', 'a+') as f:
            f.write(str_tmp)

    def draw_generator(self, x, y, input, output, gen_color, Name):

        self.create_circle(x + 6, y - 11, 10, gen_color)

        column = x // (40)
        row = y // (40)

        # Generator
        self.str_GT = str(column) + ',' + str(self.num_gen) + ',' + str(x) + ',' + str(y) + ',' + str(input) + ',' + str(output) + ',' + gen_color + ',' + Name + '\n'
        with open('create_gt.txt', 'a+') as f:
           f.write(self.str_GT)

        self.Matrix_grid[row, column] = self.num_gen
        self.Matrix_grid[row + 1, column] = self.num_gen
        self.Matrix_grid[row - 1, column] = self.num_gen
        print(self.Matrix_grid)

        row += 1
        column += 1

        #print('Create gen {} , {}'.format(row, column))

        # output
        str_tmp = ''
        #p_output_x = str(x + 17)
        #p_output_y = str(y - 10)
        if output % 2 == 0:
            for i in range(int(output / 2)):
                self.draw_line(x + 26, y - (50 + (i * 40)), x + 17, y - 10)
                self.draw_line(x + 26, y + (30 + (i * 40)), x + 17, y - 10)
                str_tmp += 'output,' + str(x + 26) + ',' + str(y - (50 + (i * 40))) + '\n'
                str_tmp += 'output,' + str(x + 26) + ',' + str(y + (30 + (i * 40))) + '\n'
        else:
            self.draw_line(x + 26, y - 10, x + 17, y - 10)
            str_tmp += 'output,' + str(x + 26) + ',' + str(y - 10) + '\n'
            for i in range(int(output / 2)):
                self.draw_line(x + 26, y - (50 + (i * 40)), x + 17, y - 10)
                self.draw_line(x + 26, y + (35 + (i * 40)), x + 17, y - 10)
                str_tmp += 'output,' + str(x + 26) + ',' + str(y - (50 + (i * 40))) + '\n'
                str_tmp += 'output,' + str(x + 26) + ',' + str(y + (35 + (i * 40))) + '\n'


        # input
        #p_input_x = str(x - 4)
        #p_input_y = str(y - 10)
        if input % 2 == 0:
            for i in range(int(input / 2)):
                self.draw_line(x - 13, y - (50 + (i * 40)), x - 4, y - 10)
                self.draw_line(x - 13, y + (30 + (i * 40)), x - 4, y - 10)
                str_tmp += 'input,' + str(x - 13) + ',' + str(y - (50 + (i * 40))) + '\n'
                str_tmp += 'input,' + str(x - 13) + ',' + str(y + (30 + (i * 40))) + '\n'
        else:
            self.draw_line(x - 13, y - 10, x - 4, y - 10)
            str_tmp += 'input,' + str(x - 13) + ',' + str(y - 10) + '\n'
            for i in range(int(input / 2)):
                self.draw_line(x - 13, y - (50 + (i * 40)), x - 4, y - 10)
                self.draw_line(x - 13, y + (35 + (i * 40)), x - 4, y - 10)
                str_tmp += 'input,' + str(x - 13) + ',' + str(y - (50 + (i * 40))) + '\n'
                str_tmp += 'input,' + str(x - 13) + ',' + str(y + (35 + (i * 40))) + '\n'

        #with open('gen_input_output_detial.txt', 'a+') as f:
            #f.write(str_tmp)

    def draw_line(self, x1, y1, x2, y2):
        self.myCanvas.create_line(x1, y1, x2, y2, fill='blue', width=2)

    def create_circle(self, x, y, r, gen_color):  # center coordinates, radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        if gen_color == 'black':
            return self.myCanvas.create_oval(x0, y0, x1, y1, fill="#000000", outline="#000000")
        else:
            return self.myCanvas.create_oval(x0, y0, x1, y1, fill="#ffffff", outline="#000000")

    def draw_twist(self, x, y):
        column = x // (40)
        row = y // (40)

        self.Matrix_grid[row, column] = -2
        self.Matrix_grid[row + 1, column] = -2
        self.Matrix_grid[row - 1, column] = -2
        print(self.Matrix_grid)

        row += 1
        column += 1

        print('Create twist {} , {}'.format(row, column))

        xt = 40 * column
        yt = 40 * row

        self.draw_line(xt + 4, yt - 55, xt - 36, yt + 30)
        self.draw_line(xt + 5, yt + 30, xt - 36, yt - 56)

    def get_input(self, x, y, column):

        Name = self.e4.get()
        print("Name", Name)

        Input = self.e5.get()
        print("Input", Input)

        Output = self.e6.get()
        print("Output", Output)

        input = self.e5.get()
        output = self.e6.get()

        if int(input) > 20 or int(output) > 20:
            tk.messagebox.showerror('error', 'Input or output should not exceed 20!', icon='error')
            return

        if Name.find('id') > -1:
            tk.messagebox.showerror('error', 'Not allowed to name object id!', icon='error')
            return

        if int(Input) < 0:
            tk.messagebox.showerror('error', 'Negative inputs not allowed!', icon='error')
            return

        if int(Output) < 0:
            tk.messagebox.showerror('error', 'Negative outputs not allowed!', icon='error')
            return

        if Name == '':
            tk.messagebox.showerror('error', 'Please enter a name for ths generator', icon='error')
            return

        generator_color = self.monthchoosen.get()

        self.counter += 1
        self.generator_dict[self.counter] = Name
        print(self.generator_dict)

        if input != '' and output != '' and self.status == 'Graph -> text':
            self.set_num_gen(self.counter)
            self.draw_generator(x, y, int(input), int(output), generator_color, Name)
            self.gen_column.append(column)
        else:
            log = Name + '|' + str(self.counter) + '|' + input + '|' + output + '|' + generator_color + '\n'
            with open('generator_info.txt', 'a+') as writer:
                writer.write(log)

        # Save string for export
        #self.str_GT += '(' + Name + ');'
        #with open('Graph_to_text.txt', 'w') as f:
         #   f.write(self.str_GT)

        self.window2.destroy()

    def get_coordinate(self, row, column):
        x = column * self.cellwidth + 4
        y = row * self.cellheight + 4
        return x, y

    def order_node(self, txt):

        # Mark id
        r = 0
        c = 0
        [rows, cols] = self.Matrix_grid.shape

        # txt = self.T.get().strip() # read input text
        Semi_colon = txt.split(';')  # split input text

        # Mark id
        for i in range(len(Semi_colon)):
            Sub_semi_colon = Semi_colon[i]
            Star = Sub_semi_colon.split('*')
            for j in range(len(Star)):
                Sub_star = Star[j].replace('(', '').replace(')', '').strip()
                if Sub_star == 'id':
                    self.Matrix_grid[r, c] = -9
                    # print(self.Matrix_grid)
                    r += 1
                else:  # is generator
                    # r = 0
                    for m in range(rows):
                        if self.Matrix_grid[m, c] > 0:
                            r += 3
                            break
                            # else:
                            # r += 1
                            # r += 3
            c += 2
            r = 0

        #print(self.Matrix_grid)

        # Order node
        for i in range(cols):
            ns = 0
            count = 0
            replace_count = 0
            for j in range(rows):
                v = self.Matrix_grid[j, i]
                if v != 0 and v != ns:
                    ns = v
                    count += 1
                    self.Matrix_order_node[j, i] = count
                    ns = self.Matrix_grid[j, i]
                    # print(self.Matrix_id_line)
                elif v != 0 and v == ns and v != -9:
                    ns = v
                    replace_count += 1
                    if replace_count >= 2:
                        replace_count = 0
                        count += 1
                        self.Matrix_order_node[j, i] = count
                        # print(self.Matrix_id_line)
                    else:
                        self.Matrix_order_node[j, i] = -7
                elif v != 0 and v == ns and v == -9:
                    ns = v
                    replace_count += 1
                    if replace_count > 0:
                        replace_count = 0
                        count += 1
                        self.Matrix_order_node[j, i] = count

        #print(self.Matrix_order_node)

        return self.Matrix_order_node, self.Matrix_grid
        # print(self.Matrix_id_line)

    def draw_line_connecting(self, M_order_node, M_grid, num_first_output, pair):

        #print("Start M_order_node : {}".format(M_order_node))
        #print("Start M_grid : {}".format(M_grid))

        M_order_node_draw_line_end = M_order_node.copy()

        x_coordinate = self.Matrix_x
        y_coordinate = self.Matrix_y
        [rows, cols] = M_order_node.shape
        M_order_node_copy = M_order_node

        # Draw id line
        for i in range(cols):
            for j in range(rows):
                x1 = x_coordinate[j, i]
                y1 = y_coordinate[j, i]
                if M_grid[j, i] == -9:
                    self.myCanvas.create_line(x1, y1 - 18, x1 - 40, y1 - 18, fill='black', width=2)

        count = 0
        inputs = 0
        outputs = 0

        # Draw connecting
        for i in range(len(pair)):

            P = pair[i]

            outputs = P[0]
            inputs = P[1]

            count += 1

            if outputs % 2 == 0 and inputs % 2 == 0 and i == 0:

                #if i == 0:

                    for j in range(rows):

                        v1 = M_order_node[j, i]
                        x1 = x_coordinate[j, i]
                        y1 = y_coordinate[j, i]

                        if v1 != 0 and v1 != -7:  # Fist couple

                            for j2 in range(rows):
                                v2 = M_order_node[j2, i + 2]
                                x2 = x_coordinate[j2, i + 2]
                                y2 = y_coordinate[j2, i + 2]

                                # draw line
                                if v1 == v2:

                                    if i >= 0:
                                        if y2 < y1:
                                            # self.draw_line(x1, y1 - 18, x2 - 40, y2 - 18)
                                            self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='red',
                                                                      width=2)
                                        elif y2 > y1:
                                            # self.draw_line(x1, y1 - 18, x2 + 40, y2 - 18)
                                            self.myCanvas.create_line(x1, y1 - 18, x2 + 40, y2 - 18, fill='red',
                                                                      width=2)
                                        else:
                                            # self.draw_line(x1, y1 - 18, x2, y2 - 18)
                                            self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='red',
                                                                      width=2)

            elif outputs % 2 == 0  and inputs % 2 == 0 and i > 0:

                #elif i > 0:

                    # adjust output
                    for s in range(rows):
                        a = M_order_node_copy[s, i]
                        b = M_grid[s, i]
                        if b != -9 and a != -7:
                            M_order_node_copy[s, i] = 0

                    cs = 0
                    for s in range(rows):
                        c = M_order_node_copy[s, i]
                        if c != 0:
                            cs += 1
                            M_order_node_copy[s, i] = cs

                    # print('M_order_node_copy : \n{}'.format(M_order_node_copy))

                    for j in range(rows):

                        v1 = M_order_node_copy[j, i]
                        x1 = x_coordinate[j, i]
                        y1 = y_coordinate[j, i]

                        if v1 != 0 and v1 != -7:  # Next couple

                            # draw connect
                            for j2 in range(rows):
                                v2 = M_order_node[j2, i + 2]
                                x2 = x_coordinate[j2, i + 2]
                                y2 = y_coordinate[j2, i + 2]

                                # draw line
                                if v1 == v2:

                                    if i >= 0:
                                        if y2 < y1:
                                            # self.draw_line(x1, y1 - 18, x2 - 40, y2 - 18)
                                            self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='green',
                                                                      width=2)
                                        elif y2 > y1:
                                            # self.draw_line(x1, y1 - 18, x2 + 40, y2 - 18)
                                            self.myCanvas.create_line(x1, y1 - 18, x2 + 40, y2 - 18, fill='green',
                                                                      width=2)
                                        else:
                                            # self.draw_line(x1, y1 - 18, x2, y2 - 18)
                                            self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='green',
                                                                      width=2)

            elif outputs % 2 != 0 and inputs % 2 != 0 and i == 0:

                #if i >= 0:

                    print("01 - outputs % 2 != 0 and inputs % 2 != 0 and i == 0")

                    # adjust output
                    for s in range(rows):
                        a = M_order_node_copy[s, i]
                        b = M_grid[s, i]
                        if b != -9 and a != -7:
                            M_order_node_copy[s, i] = 0

                    cs = 0
                    for s in range(rows):
                        c = M_order_node_copy[s, i]
                        if c != 0:
                            cs += 1
                            M_order_node_copy[s, i] = cs
                    if i == 0:
                        a = 1

                    print('Modulus > 0 , M_order_node_copy : \n{}'.format(M_order_node_copy))

                    for j in range(rows):

                        v1 = M_order_node_copy[j, i]
                        x1 = x_coordinate[j, i]
                        y1 = y_coordinate[j, i]

                        if v1 != 0 and v1 != -7:  # Next couple

                            # draw connect
                            for j2 in range(rows):
                                v2 = M_order_node[j2, i + 2]
                                x2 = x_coordinate[j2, i + 2]
                                y2 = y_coordinate[j2, i + 2]

                                # draw line
                                if v2 == -7: #v1 == v2:

                                    if i >= 0:
                                        if y2 < y1:
                                            # self.draw_line(x1, y1 - 18, x2 - 40, y2 - 18)
                                            self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='yellow',
                                                                      width=2)
                                        elif y2 > y1:
                                            # self.draw_line(x1, y1 - 18, x2 + 40, y2 - 18)
                                            self.myCanvas.create_line(x1, y1 - 18, x2 + 40, y2 - 18, fill='yellow',
                                                                      width=2)
                                        else:
                                            # self.draw_line(x1, y1 - 18, x2, y2 - 18)
                                            self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='pink',
                                                                      width=2)

            elif outputs % 2 != 0 and inputs % 2 != 0 and i > 0:

                print('02 - outputs % 2 != 0 and inputs % 2 != 0 and i')

                # adjust output
                for s in range(rows):
                    a = M_order_node_copy[s, i]
                    b = M_grid[s, i]
                    if b != -9 and a != -7:
                        M_order_node_copy[s, i] = 0

                cs = 0
                for s in range(rows):
                    c = M_order_node_copy[s, i]
                    if c != 0:
                        cs += 1
                        M_order_node_copy[s, i] = cs

                # print('M_order_node_copy : \n{}'.format(M_order_node_copy))

                for j in range(rows):

                    v1 = M_order_node_copy[j, i]
                    x1 = x_coordinate[j, i]
                    y1 = y_coordinate[j, i]

                    if v1 != 0 and v1 != -7:  # Next couple

                        # draw connect
                        for j2 in range(rows):
                            v2 = M_order_node[j2, i + 2]
                            x2 = x_coordinate[j2, i + 2]
                            y2 = y_coordinate[j2, i + 2]

                            # draw line
                            if v2 == -7: #v1 == v2:

                                if i >= 0:
                                    if y2 < y1:
                                        # self.draw_line(x1, y1 - 18, x2 - 40, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='green',
                                                                  width=2)
                                    elif y2 > y1:
                                        # self.draw_line(x1, y1 - 18, x2 + 40, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 + 40, y2 - 18, fill='green',
                                                                  width=2)
                                    else:
                                        # self.draw_line(x1, y1 - 18, x2, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='green',
                                                                  width=2)

            elif outputs % 2 == 0 and inputs % 2 != 0 and i == 0:
                print("1 - outputs % 2 == 0 and inputs % 2 != 0 and i == 0")

                i *= 2

                # adjust output
                for s in range(rows):
                    a = M_order_node_copy[s, i]
                    b = M_grid[s, i]
                    if b != -9 and a != -7:
                        M_order_node_copy[s, i] = 0

                cs = 0
                for s in range(rows):
                    c = M_order_node_copy[s, i]
                    if c != 0:
                        cs += 1
                        M_order_node_copy[s, i] = cs

                # print('M_order_node_copy : \n{}'.format(M_order_node_copy))

                for j in range(rows):

                    v1 = M_order_node_copy[j, i]
                    x1 = x_coordinate[j, i]
                    y1 = y_coordinate[j, i]

                    if v1 != 0 and v1 != -7:  # Next couple

                        # draw connect
                        for j2 in range(rows):
                            v2 = M_order_node[j2, i + 2]
                            x2 = x_coordinate[j2, i + 2]
                            y2 = y_coordinate[j2, i + 2]

                            # draw line
                            if v1 == v2:

                                if i >= 0:
                                    if y2 < y1:
                                        # self.draw_line(x1, y1 - 18, x2 - 40, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='pink',
                                                                  width=2)
                                    elif y2 > y1:
                                        # self.draw_line(x1, y1 - 18, x2 + 40, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 + 40, y2 - 18, fill='pink',
                                                                  width=2)
                                    else:
                                        # self.draw_line(x1, y1 - 18, x2, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='pink',
                                                                  width=2)

            elif outputs % 2 == 0 and inputs % 2 != 0 and i > 0:
                print("2 - outputs % 2 == 0 and inputs % 2 != 0 and i > 0")

                i *= 2

                # adjust output
                for s in range(rows):
                    a = M_order_node_copy[s, i]
                    b = M_grid[s, i]
                    if b != -9 and a != -7:
                        M_order_node_copy[s, i] = 0

                cs = 0
                for s in range(rows):
                    c = M_order_node_copy[s, i]
                    if c != 0:
                        cs += 1
                        M_order_node_copy[s, i] = cs

                # print('M_order_node_copy : \n{}'.format(M_order_node_copy))

                for j in range(rows):

                    v1 = M_order_node_copy[j, i]
                    x1 = x_coordinate[j, i]
                    y1 = y_coordinate[j, i]

                    if v1 != 0 and v1 != -7:  # Next couple

                        # draw connect
                        for j2 in range(rows):
                            v2 = M_order_node[j2, i + 2]
                            x2 = x_coordinate[j2, i + 2]
                            y2 = y_coordinate[j2, i + 2]

                            # draw line
                            if v1 == v2:

                                if i >= 0:
                                    if y2 < y1:
                                        # self.draw_line(x1, y1 - 18, x2 - 40, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='pink',
                                                                  width=2)
                                    elif y2 > y1:
                                        # self.draw_line(x1, y1 - 18, x2 + 40, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 + 40, y2 - 18, fill='pink',
                                                                  width=2)
                                    else:
                                        # self.draw_line(x1, y1 - 18, x2, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='pink',
                                                                  width=2)

            elif outputs % 2 != 0 and inputs % 2 == 0 and i == 0:
                print("3 - outputs % 2 != 0 and inputs % 2 == 0 and i == 0")

                i *= 2

                # adjust output
                for s in range(rows):
                    a = M_order_node_copy[s, i]
                    b = M_grid[s, i]
                    if b != -9 and a != -7:
                        M_order_node_copy[s, i] = 0

                cs = 0
                for s in range(rows):
                    c = M_order_node_copy[s, i]
                    if c != 0:
                        cs += 1
                        M_order_node_copy[s, i] = cs

                # print('M_order_node_copy : \n{}'.format(M_order_node_copy))

                for j in range(rows):

                    v1 = M_order_node_copy[j, i]
                    x1 = x_coordinate[j, i]
                    y1 = y_coordinate[j, i]

                    if v1 != 0 and v1 != -7:  # Next couple

                        # draw connect
                        for j2 in range(rows):
                            v2 = M_order_node[j2, i + 2]
                            x2 = x_coordinate[j2, i + 2]
                            y2 = y_coordinate[j2, i + 2]

                            # draw line
                            if v1 == v2:

                                if i >= 0:
                                    if y2 < y1:
                                        # self.draw_line(x1, y1 - 18, x2 - 40, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='pink',
                                                                  width=2)
                                    elif y2 > y1:
                                        # self.draw_line(x1, y1 - 18, x2 + 40, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 + 40, y2 - 18, fill='pink',
                                                                  width=2)
                                    else:
                                        # self.draw_line(x1, y1 - 18, x2, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='pink',
                                                                  width=2)

            elif outputs % 2 != 0 and inputs % 2 == 0 and i > 0:
                print("4 - outputs % 2 != 0 and inputs % 2 == 0 and i > 0")

                i *= 2

                # adjust output
                for s in range(rows):
                    a = M_order_node_copy[s, i]
                    b = M_grid[s, i]
                    if b != -9 and a != -7:
                        M_order_node_copy[s, i] = 0

                cs = 0
                for s in range(rows):
                    c = M_order_node_copy[s, i]
                    if c != 0:
                        cs += 1
                        M_order_node_copy[s, i] = cs

                # print('M_order_node_copy : \n{}'.format(M_order_node_copy))

                for j in range(rows):

                    v1 = M_order_node_copy[j, i]
                    x1 = x_coordinate[j, i]
                    y1 = y_coordinate[j, i]

                    if v1 != 0 and v1 != -7:  # Next couple

                        # draw connect
                        for j2 in range(rows):
                            v2 = M_order_node[j2, i + 2]
                            x2 = x_coordinate[j2, i + 2]
                            y2 = y_coordinate[j2, i + 2]

                            # draw line
                            if v1 == v2:

                                if i >= 0:
                                    if y2 < y1:
                                        # self.draw_line(x1, y1 - 18, x2 - 40, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='yellow',
                                                                  width=2)
                                    elif y2 > y1:
                                        # self.draw_line(x1, y1 - 18, x2 + 40, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 + 40, y2 - 18, fill='yellow',
                                                                  width=2)
                                    else:
                                        # self.draw_line(x1, y1 - 18, x2, y2 - 18)
                                        self.myCanvas.create_line(x1, y1 - 18, x2 - 40, y2 - 18, fill='yellow',
                                                                  width=2)


        print('Last output : {}'.format(outputs))

        if outputs == 1:

            # Draw line end
            M_order_node_copy = M_order_node_draw_line_end
            print('M_order_node_copy : \n{}'.format(M_order_node_copy))
            print('Draw line end')
            [r, c] = M_order_node_copy.shape
            col_ind = 0
            for i in range(r - 1, -1, -1):
                #print(M_order_node_copy[:, i])
                #print(sum(M_order_node_copy[:, i]))
                if sum(M_order_node_copy[:, i]) != 0:
                    col_ind = i
                    for j in range(r):
                        #print(M_order_node_copy[:, col_ind])
                        if M_order_node_copy[j, col_ind] < 0:
                            x1 = x_coordinate[j, col_ind]
                            y1 = y_coordinate[j, col_ind] - 18
                            x2 = x_coordinate[j, c - 1]
                            y2 = y1
                            self.myCanvas.create_line(x1, y1, x2, y2, fill='orange', width=2)
                    break

        elif outputs > 1:

            # Draw line end
            M_order_node_copy = M_order_node_draw_line_end
            print('M_order_node_copy : \n{}'.format(M_order_node_copy))
            print('Draw line end')
            [r, c] = M_order_node_copy.shape
            col_ind = 0
            for i in range(r - 1, -1, -1):
                #print(M_order_node_copy[:, i])
                #print(sum(M_order_node_copy[:, i]))
                if sum(M_order_node_copy[:, i]) != 0:
                    col_ind = i
                    for j in range(r - 1):
                        #print(M_order_node_copy[:, col_ind])
                        if M_order_node_copy[j + 1, col_ind] > M_order_node_copy[j, col_ind] and M_order_node_copy[j, col_ind] > 0:
                            x1 = x_coordinate[j, col_ind]
                            y1 = y_coordinate[j, col_ind] - 18
                            x2 = x_coordinate[j, c - 1]
                            y2 = y1
                            self.myCanvas.create_line(x1, y1, x2, y2, fill='orange', width=2)
                        if M_order_node_copy[j + 1, col_ind] < M_order_node_copy[j, col_ind] and M_order_node_copy[j, col_ind] > 0:
                            x1 = x_coordinate[j, col_ind]
                            y1 = y_coordinate[j, col_ind] - 18
                            x2 = x_coordinate[j, c - 1]
                            y2 = y1
                            self.myCanvas.create_line(x1, y1, x2, y2, fill='orange', width=2)
                    break

    def create_graph_of_text(self):

        x_coordinate = self.Matrix_x
        y_coordinate = self.Matrix_y

        #if path.exists('pair.txt'):
            #os.remove('pair.txt')

        #print(self.Matrix_grid)

        pair = []
        sub_pair = [0, 0]
        str_pair = []
        sub_str_pair = [[], []]
        count_pair = 0

        # read string diagram
        with open('generator_info.txt') as reader:
            content = reader.readlines()

        row = 2
        column = 1
        x = 34
        y = 75
        do_first = False
        have_gen = False
        have_id = False
        output_prev = 0
        detect_first_output = False
        num_first_output = 0

        txt = self.T.get().strip() # read input text
        Semi_colon = txt.split(';') # split input text

        # Split semi colon
        for i in range(len(Semi_colon)):

            row = 2

            Sub_semi_colon = Semi_colon[i]
            #print('Sub_semi_colon : {}'.format(Sub_semi_colon))
            Star = Sub_semi_colon.split('*')

            find_id = Sub_semi_colon.find('id') # find have id

            # Split star
            for j in range(len(Star)):
                Sub_star = Star[j].replace('(', '').replace(')', '').strip()
                if Sub_star == 'id': # id

                    have_id = True
                    row += 1

                else:
                    for k in range(len(content)): # genenrator name

                        E = content[k].split('|')
                        Name = E[0]
                        input = int(E[2])
                        output = int(E[3])
                        generator_color = E[4].rstrip()
                        if Name == Sub_star:

                            #column += 2

                            if not detect_first_output:
                                num_first_output = output
                                detect_first_output = True

                            # draw generator
                            x1 = column * 40
                            y1 = row * 40
                            dx = x - x1
                            dy = y - y1

                            x = x - dx - 22
                            y = y - dy - 4

                            self.counter_text += 1
                            self.generator_dict[self.counter_text] = Name
                            self.set_num_gen(self.counter_text)
                            #self.draw_generator_TG(x, y, input, output, generator_color, Name)
                            self.draw_generator(x, y, input, output, generator_color, Name)
                            self.gen_column.append(column)

                            row += 3

                            print("self.Matrix_grid : \n{}".format(self.Matrix_grid))

                            #column += 2

                            #print(self.Matrix_grid)
                            #print(self.counter_text)
                            #print("column : {}".format(column))

                            # Map pair output - input
                            count_pair += 1

                            if count_pair == 1:
                                #sub_pair.append([output])
                                #sub_str_pair.append([Name, 'output'])
                                sub_str_pair[0] = [Name, 'output']
                                sub_pair[0]= output
                            elif count_pair == 2:

                                #sub_pair.append([input])
                                sub_pair[1] = input
                                pair.append(sub_pair)
                                sub_pair = [0, 0]
                                sub_pair[0] = output

                                #sub_pair.append([output])

                                #sub_str_pair.append([Name, 'input'])

                                sub_str_pair[1] = [Name, 'input']
                                str_pair.append(sub_str_pair)
                                sub_str_pair = [[], []]
                                sub_str_pair[0] = [Name, 'output']

                                #sub_str_pair.append([Name, 'output'])
                                #str_pair.append([Name, 'output'])

                                count_pair = 1

                            break

            column += 2

        print("self.Matrix_grid : \n{}".format(self.Matrix_grid))

        str_pair.append(sub_str_pair)
        pair.append(sub_pair)

        # Draw line connecting
        M_order_node, M_grid = self.order_node(txt)
        #self.draw_line_connecting(M_order_node, M_grid, num_first_output, str_pair, pair)
        self.draw_line_connecting(M_order_node, M_grid, num_first_output, pair)

        print("M_order_node : \n{}".format(M_order_node))
        print("M_grid : \n{}".format(M_grid))

        self.window3.destroy()

        #self.myCanvas.create_text(400, 705, fill="red", font="Arial 20 bold",
                                  #text=txt)

        #print(self.Matrix_grid)
        #print(pair)
        #print(str_pair)

    def click_right_button(self, eventorigin):

        if self.status == 'Graph -> text':
            if self.twist_status:
                self.create_twist(eventorigin)
        else:

            # Sub figure
            self.window3 = tk.Tk()
            self.window3.title("Generator created")
            self.window_height = 240
            self.window_width = 330

            self.screen_width = self.window3.winfo_screenwidth()
            self.screen_height = self.window3.winfo_screenheight()

            self.x_coordinate = int((self.screen_width / 2) - (self.window_width / 2))
            self.y_coordinate = int((self.screen_height / 2) - (self.window_height / 2))

            self.window3.geometry(
                "{}x{}+{}+{}".format(self.window_width, self.window_height, self.x_coordinate, self.y_coordinate))

            TitleLabel = ttk.Label(self.window3)

            listNodes = Listbox(self.window3, width=50, height=10)
            listNodes.place(x=0, y=0)

            scrollbar = Scrollbar(self.window3, orient="vertical")
            scrollbar.config(command=listNodes.yview)
            scrollbar.place(x=305, y=0)

            listNodes.config(yscrollcommand=scrollbar.set)

            with open('generator_info.txt') as reader:
                content = reader.readlines()
            for i in range(len(content)):
                A = content[i].split('|')
                tmp = 'Name : ' + A[0] + ' , Input : ' + A[2] + ' , Output : '+ A[3] + ' , Color : ' + A[4]
                listNodes.insert(END, tmp)

            self.T = Entry(self.window3, width=43)
            self.T.place(x=40, y=170, bordermode="outside")

            l = Label(self.window3, text="Text : ")
            l.place(x=5, y=170, bordermode="outside")

            btn = ttk.Button(self.window3, text="Apply", command=self.create_graph_of_text)
            btn.place(x=228, y=200, bordermode="outside")

    def create_twist(self, eventorigin):

        x = eventorigin.x
        y = eventorigin.y

        column = x // (40)
        row = y // (40)

        row += 1
        column += 1

        self.draw_twist(x, y)

        print("Click ", (x, y), "coordinates: ", row, column)

        self.gen_column.append(column)

    def getorigin(self, eventorigin):

        if self.mode == 'connecting' and not self.Clicked:
            self.Clicked = True
            #print('Click true!')
            print('Click start line !')
            self.sub_line_intersection.append([eventorigin.x, eventorigin.y])
        elif  self.mode == 'connecting' and self.Clicked:
            self.Clicked = False
            #print('Click false !')
            print('Click stop line !')
            self.sub_line_intersection.append([eventorigin.x, eventorigin.y])
            self.line_intersection.append(self.sub_line_intersection)
            self.sub_line_intersection = []

            # Check have twist
            if len(self.line_intersection) == 2:
                line_1 = self.line_intersection[0]
                line_2 = self.line_intersection[1]
                point_line1_1 = line_1[0]
                point_line1_2 = line_1[1]
                point_line2_1 = line_2[0]
                point_line2_2 = line_2[1]
                self.line_intersection = []
                point_of_intersection = self.check_intersection_line(point_line1_1, point_line1_2, point_line2_1, point_line2_2)
                if len(point_of_intersection) == 2:
                    x_intersection = point_of_intersection[0]
                    y_intersection = point_of_intersection[1]
                    column_intersection = int(x_intersection // (40))
                    row_intersection = int(y_intersection // (40))
                    print("column_intersection : {} , row_intersection : {}".format(column_intersection, row_intersection))
                    self.Matrix_grid[:, column_intersection] = 0
                    self.Matrix_grid[row_intersection, column_intersection] = -2
                    self.gen_column.append(column_intersection + 1)
                    print(self.Matrix_grid)


            # Twist detection
            #A = self.line_intersection[0]
            #print(A[0])
            #print(A[1])

        x = eventorigin.x
        y = eventorigin.y

        column = x // (40)
        row = y // (40)

        # Remove generator or id
        if self.status_remove == True:

            # assign matrix
            self.status_remove = False
            self.Matrix_grid[row, column] = 0
            self.Matrix_grid[row + 1, column] = 0
            self.Matrix_grid[row - 1, column] = 0
            print('Remove :{}\n'.format(self.Matrix_grid))

            # clear canvas
            self.myContainer1.destroy()
            self.myContainer1 = tk.Frame(self.myParent)
            self.myContainer1.pack()
            self.draw_grid(20, 20)
            self.myCanvas.update()

            # delete text gen
            tmp = ''
            with open("create_gt.txt", 'r') as file_in:
                for line in file_in:
                    str = line.split(',')
                    s_column = int(str[0])
                    if column != s_column:
                        tmp += line

            # save of delete
            with open('create_gt.txt', 'w') as f:
                f.write(tmp)

            # redraw generator
            with open("create_gt.txt", 'r') as file_in:
                for line in file_in:
                    str = line.split(',')
                    column = int(str[0])
                    num_gen = int(str[1])
                    x = int(str[2])
                    y = int(str[3])
                    input = int(str[4])
                    output = int(str[5])
                    gen_color = str[6]
                    name = str[7].replace('\n', '')
                    self.draw_generator_of_remove(x, y, input, output, gen_color, name)

            # redraw id
            x_coordinate = self.Matrix_x
            y_coordinate = self.Matrix_y

            [r, c] = self.Matrix_grid.shape
            for j in range(r):
                for i in range(c):
                    if self.Matrix_grid[j, i] == -1:
                        x1 = x_coordinate[j, i]
                        y1 = y_coordinate[j, i]
                        self.myCanvas.create_line(x1, y1 - 18, x1 - 40, y1 - 18, fill='blue', width=2)

            return

        # End remove or id


        row += 1
        column += 1

        print("Click ", (x, y), "coordinates: ", row, column)
        print(self.mode)

        if  self.mode == 'connecting':
            self.line_position.append(x)
            self.line_position.append(y)
            if len(self.line_position) == 4:
                self.draw_line(self.line_position[0], self.line_position[1], self.line_position[2], self.line_position[3])
                self.line_position = [self.line_position[2], self.line_position[3]]
            else:
                print('Points to points : {}'.format(self.line_position))
        else:

            W = 40
            H = 40

            x1 = column * 40
            y1 = row * 40
            dx = x - x1
            dy = y - y1

            x = x - dx - 22
            y = y - dy - 4
            # print('x : {} , y : {}'.format(x, y))

            #panel.place(x=x, y=y)

            if self.status_remove == False:

                # Sub figure
                self.window2 = tk.Tk() # Toplevel(self.myParent)
                self.window2.title("Generator creator")
                self.window_height = 200
                self.window_width = 260

                self.screen_width = self.window2.winfo_screenwidth()
                self.screen_height = self.window2.winfo_screenheight()

                self.x_coordinate = int((self.screen_width / 2) - (self.window_width / 2))
                self.y_coordinate = int((self.screen_height / 2) - (self.window_height / 2))

                self.window2.geometry("{}x{}+{}+{}".format(self.window_width, self.window_height, self.x_coordinate, self.y_coordinate))

                TitleLabel = ttk.Label(self.window2)

                L4 = ttk.Label(self.window2, text = "Name : ", justify=RIGHT)
                L4.place(x=30, y=20)

                self.e4 = ttk.Entry(self.window2, width = 20)
                self.e4.place(x=80, y=20, bordermode="outside")

                L5 = ttk.Label(self.window2, text = "Input : ", justify=RIGHT)
                L5.place(x=30, y=45)

                self.e5 = ttk.Entry(self.window2, width = 20)
                self.e5.place(x=80, y=45, bordermode="outside")

                L6 = ttk.Label(self.window2, text = "Output : ", justify=RIGHT)
                L6.place(x=20, y=70, bordermode="outside")

                self.e6 = ttk.Entry(self.window2, width = 20)
                self.e6.place(x=80, y=70, bordermode="outside")

                L7 = ttk.Label(self.window2, text = "Color : ", justify=RIGHT)
                L7.place(x=30, y=95)

                #self.variable = StringVar(self.window2)
                #self.variable.set("one")  # default value

                #gen_color = tk.StringVar()
                self.monthchoosen = ttk.Combobox(self.window2, width=10, value = ['black', 'white'])
                self.monthchoosen.current(0)
                self.monthchoosen.place(x=80, y=95, bordermode="outside")

                btn = ttk.Button(self.window2, text = "Apply", command = lambda:self.get_input(x, y, column))
                btn.place(x=80, y=130, bordermode="outside")

    def calculate(self):
        #global var, gen_column
        M = self.get_Matrix_grid()

        c = 0
        tmp = ''
        log = 0
        [row, col] = M.shape
        self.gen_column = list(dict.fromkeys(self.gen_column))
        self.gen_column = sorted(self.gen_column)
        for i in range(len(self.gen_column)):
            tmp += '('
            log = ''
            for j in range(row):
                if M[j, self.gen_column[i] - 1] == -1:
                    tmp += 'id * '
                elif M[j, self.gen_column[i] - 1] == -2 and M[j, self.gen_column[i] - 1] != log:
                    log = M[j, self.gen_column[i] - 1]
                    tmp += 'twist * '
                elif M[j, self.gen_column[i] - 1] != 0 and M[j, self.gen_column[i] - 1] != log:
                    log = M[j, self.gen_column[i] - 1]
                    tmp += str(self.generator_dict.get(M[j, self.gen_column[i] - 1])) + ' * '
            tmp = tmp[:-3]
            tmp += ') ; '

        print(tmp)


        '''
        # check count
        count = tmp.count(';')
        if count <= 1:
            tmp = tmp.replace(';', '')
        '''

        tmp = tmp.strip()[:-1]
        if len(tmp) < 4:
            tmp = ''
            messagebox.showinfo("Result", "Null")
        else:
            messagebox.showinfo("Result", tmp)

        #var.set(tmp)
        #print(len(tmp))

    def connecting(self):

        self.mode = 'connecting'
        self.Clicked = False
        self.line_position = []

    def cursor(self):
        self.mode = ''

    def twist(self):
        self.twist_status = True

def on_tab_selected(event, TAB1, TAB2):

    global draw_tab_1, draw_tab_2, grid_tab_1, grid_tab_2

    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")
    if tab_text == 'Graph -> text' and not draw_tab_1:
        myapp = GridWindow(TAB1, 'Graph -> text')
        if grid_tab_1 == False:
            myapp.draw_grid(20, 20)
            grid_tab_1 = True
        draw_tab_1 = True
        draw_tab_2 = False
    elif tab_text == 'Text -> graph' and not draw_tab_2:
        myapp = GridWindow(TAB2, 'Text -> graph')
        if grid_tab_2 == False:
            myapp.draw_grid(20, 20)
            grid_tab_2 = True
        draw_tab_2 = True
        draw_tab_1 = False

        if path.exists('gen_input_output_detial.txt'):
            os.remove('gen_input_output_detial.txt')

        #MsgBox = tk.messagebox.askquestion('delete', 'Delete old generator ?', icon='warning')
        #if MsgBox == 'yes':
         #   os.remove('generator_info.txt')

if __name__ == '__main__':

    if path.exists('create_gt.txt'):
        os.remove('create_gt.txt')

    if path.exists('graph_to_text_export.txt'):
        os.remove('graph_to_text_export.txt')

    draw_tab_1 = False
    draw_tab_2 = False
    grid_tab_1 = False
    grid_tab_2 = False


    # GUI
    mainWindow = tk.Tk()
    mainWindow.title('[ Graph to text ] and  [ Text to graph ]')
    mainWindow.resizable(width=False, height=False)

    window_height = 840
    window_width = 820

    screen_width = mainWindow.winfo_screenwidth()
    screen_height = mainWindow.winfo_screenheight()

    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))

    mainWindow.geometry("{}x{}+{}+{}".format(window_width, window_height, x_coordinate, y_coordinate))

    TAB_CONTROL = ttk.Notebook(mainWindow)

    TAB1 = ttk.Frame(TAB_CONTROL)
    TAB2 = ttk.Frame(TAB_CONTROL)

    TAB_CONTROL.add(TAB1, text='Graph -> text')
    TAB_CONTROL.add(TAB2, text='Text -> graph')

    TAB_CONTROL.pack(expand=1, fill="both")

    #var = StringVar()
    #T = Entry(mainWindow, textvariable = var, width = 90)
    #T.place(x=265, y=835, bordermode="outside")

    #l = Label(mainWindow, text="Result : ")
    #l.config(font=("Courier", 10))
    #l.place(x=210, y=835, bordermode="outside")

    TAB_CONTROL.bind("<<NotebookTabChanged>>", lambda event: on_tab_selected(event, TAB1, TAB2))

    mainWindow.mainloop()