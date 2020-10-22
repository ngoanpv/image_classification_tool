import pandas as pd
import os
import numpy as np
import glob
import argparse
import tkinter as tk
import os
from shutil import copyfile, move
from PIL import ImageTk, Image

#CONFIG

input_folder_pattern = '/home/ngoanpv/work/datalab/liveness/fecredit_test/pass_quality/**/'
labels = ["live_good", "live_bad", "spoof", "noise"]
# provide either 'copy' or 'move', depending how you want to sort the images into the new folders
# - 'move' starts where you left off last time sorting, no 'go to #pic', works with number-buttons for labeling, no txt-file for tracking after closing GUI, saves memory
# - 'copy' starts always at beginning, has 'go to #pic', doesn't work with number-buttons, has a txt-for tracking the labels after closing the GUI
copy_or_move = 'copy'
df_path = '/home/ngoanpv/work/datalab/liveness/fecredit_test/tracking_set1.txt'
# a selection of what file-types to be sorted, anything else will be excluded
file_extensions = ['*.jpg', '*.png', '*.jpeg']
resize = False
ROOT_DES_PATH = "/home/ngoanpv/work/datalab/liveness/fecredit_test/labeled/set1/"

class ImageGui:
    """
    GUI for iFind1 image sorting. This draws the GUI and handles all the events.
    Useful, for sorting views into sub views or for removing outliers from the data.
    """

    def __init__(self, master, labels, paths):
        """
        Initialise GUI
        :param master: The parent window
        :param labels: A list of labels that are associated with the images
        :param paths: A list of file paths to images
        :return:
        """

        # So we can quit the window from within the functions
        self.master = master

        # Extract the frame so we can draw stuff on it
        frame = tk.Frame(master)

        # Initialise grid
        frame.grid()

        # Start at the first file name
        self.index = 0
        self.paths = paths
        self.labels = labels
        #### added in version 2
        self.sorting_label = 'unsorted'
        ####

        # Number of labels and paths
        self.n_labels = len(labels)
        self.n_paths = len(paths)

        # Set empty image container
        self.image_raw = None
        self.image = None
        self.image_panel = tk.Label(frame)

        # set image container to first image
        self.set_image(paths[self.index])

        # Make buttons
        self.buttons = []
        for label in labels:
            self.buttons.append(
                    tk.Button(frame, text=label, width=10, height=2, fg='blue', command=lambda l=label: self.vote(l))
            )
            
        ### added in version 2
        self.buttons.append(tk.Button(frame, text="prev im", width=10, height=1, fg="green", command=lambda l=label: self.move_prev_image()))
        self.buttons.append(tk.Button(frame, text="next im", width=10, height=1, fg='green', command=lambda l=label: self.move_next_image()))
        ###
        
        # Add progress label
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label = tk.Label(frame, text=progress_string, width=10)
        
        # Place buttons in grid
        for ll, button in enumerate(self.buttons):
            button.grid(row=0, column=ll, sticky='we')
            #frame.grid_columnconfigure(ll, weight=1)

        # Place progress label in grid
        self.progress_label.grid(row=0, column=self.n_labels+2, sticky='we') # +2, since progress_label is placed after
                                                                            # and the additional 2 buttons "next im", "prev im"
            
        #### added in version 2
        # Add sorting label
        sorting_string = os.path.split(df.sorted_in_folder[self.index])[-2]
        self.sorting_label = tk.Label(frame, text=("in folder: %s" % (sorting_string)), width=15)
        
        # Place typing input in grid, in case the mode is 'copy'
        if copy_or_move == 'copy':
            tk.Label(frame, text="go to #pic:").grid(row=1, column=0)

            self.return_ = tk.IntVar() # return_-> self.index
            self.return_entry = tk.Entry(frame, width=6, textvariable=self.return_)
            self.return_entry.grid(row=1, column=1, sticky='we')
            master.bind('<Return>', self.num_pic_type)
        ####
        
        # Place sorting label in grid
        self.sorting_label.grid(row=2, column=self.n_labels+1, sticky='we') # +2, since progress_label is placed after
                                                                            # and the additional 2 buttons "next im", "prev im"
        # Place the image in grid
        self.image_panel.grid(row=2, column=0, columnspan=self.n_labels+1, sticky='we')

        # key bindings (so number pad can be used as shortcut)
        # make it not work for 'copy', so there is no conflict between typing a picture to go to and choosing a label with a number-key
        if copy_or_move == 'move':
            for key in range(self.n_labels):
                master.bind(str(key+1), self.vote_key)

    def show_next_image(self):
        """
        Displays the next image in the paths list and updates the progress display
        """
        self.index += 1
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        
        #### added in version 2
        sorting_string = os.path.split(df.sorted_in_folder[self.index])[-2] #shows the last folder in the filepath before the file
        self.sorting_label.configure(text=("in folder: %s" % (sorting_string)))
        ####

        if self.index < self.n_paths:
            self.set_image(df.sorted_in_folder[self.index])
        else:
            self.master.quit()
    
    ### added in version 2        
    def move_prev_image(self):
        """
        Displays the prev image in the paths list AFTER BUTTON CLICK,
        doesn't update the progress display
        """
        self.index -= 1
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        
        sorting_string = os.path.split(df.sorted_in_folder[self.index])[-2] #shows the last folder in the filepath before the file
        self.sorting_label.configure(text=("in folder: %s" % (sorting_string)))
        
        if self.index < self.n_paths:
            self.set_image(df.sorted_in_folder[self.index]) # change path to be out of df
        else:
            self.master.quit()
    
    ### added in version 2
    def move_next_image(self):
        """
        Displays the next image in the paths list AFTER BUTTON CLICK,
        doesn't update the progress display
        """
        self.index += 1
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        sorting_string = os.path.split(df.sorted_in_folder[self.index])[-2] #shows the last folder in the filepath before the file
        self.sorting_label.configure(text=("in folder: %s" % (sorting_string)))
        
        if self.index < self.n_paths:
            self.set_image(df.sorted_in_folder[self.index])
        else:
            self.master.quit()

    def set_image(self, path):
        """
        Helper function which sets a new image in the image view
        :param path: path to that image
        """
        image = self._load_image(path)
        self.image_raw = image
        self.image = ImageTk.PhotoImage(image)
        self.image_panel.configure(image=self.image)

    def vote(self, label):
        """
        Processes a vote for a label: Initiates the file copying and shows the next image
        :param label: The label that the user voted for
        """
        ##### added in version 2
        # check if image has already been sorted (sorted_in_folder != 0)
        if df.sorted_in_folder[self.index] != df.im_path[self.index]:
            # if yes, use as input_path the current location of the image
            input_path = df.sorted_in_folder[self.index]
            root_ext, file_name = os.path.split(input_path)
            root, _ = os.path.split(root_ext)
        else:
            # if image hasn't been sorted use initial location of image
            input_path = df.im_path[self.index]
            root, file_name = os.path.split(input_path)
        #####
        
        #input_path = self.paths[self.index]
        if copy_or_move == 'copy':
            self._copy_image(label, self.index)
        if copy_or_move == 'move':
            self._move_image(label, self.index)
            
        self.show_next_image()

    def vote_key(self, event):
        """
        Processes voting via the number key bindings.
        :param event: The event contains information about which key was pressed
        """
        pressed_key = int(event.char)
        label = self.labels[pressed_key-1]
        self.vote(label)
    
    #### added in version 2
    def num_pic_type(self, event):
        """Function that allows for typing to what picture the user wants to go.
        Works only in mode 'copy'."""
        # -1 in line below, because we want images bo be counted from 1 on, not from 0
        self.index = self.return_.get() - 1
        
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        sorting_string = os.path.split(df.sorted_in_folder[self.index])[-2] #shows the last folder in the filepath before the file
        self.sorting_label.configure(text=("in folder: %s" % (sorting_string)))
        
        self.set_image(df.sorted_in_folder[self.index])

    @staticmethod
    def _load_image(path):
        """
        Loads and resizes an image from a given path using the Pillow library
        :param path: Path to image
        :return: Resized or original image 
        """
        image = Image.open(path)
        im_width, im_height = image.size
        if(resize or im_width>1000 or im_height > 1000):
            max_height = 500
            img = image 
            s = img.size
            ratio = max_height / s[1]
            image = img.resize((int(s[0]*ratio), int(s[1]*ratio)), Image.ANTIALIAS)
        return image

    @staticmethod
    def _copy_image(label, ind):
        """
        Copies a file to a new label folder using the shutil library. The file will be copied into a
        subdirectory called label in the input folder.
        :param input_path: Path of the original image
        :param label: The label
        """
        import datetime

        now = str(datetime.datetime.now())[:19]
        now = now.replace(":", "_")

        root, file_name = os.path.split(df.sorted_in_folder[ind])
        # two lines below check if the filepath contains as an ending a folder with the name of one of the labels
        # if so, this folder is being cut out of the path
        if os.path.split(root)[1] in labels:
            root = os.path.split(root)[0]
            os.remove(df.sorted_in_folder[ind])

        name, ext = file_name.split('.')
        name = name + '_' + now + '.' + ext
        output_path = os.path.join(ROOT_DES_PATH, label, name)
        print("file_name =",file_name)
        print(" %s --> %s" % (file_name, label))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        copyfile(df.im_path[ind], output_path)
        # keep track that the image location has been changed by putting the new location-path in sorted_in_folder    
        df.loc[ind, 'sorted_in_folder'] = output_path
        #####
        df.to_csv(df_path)

    @staticmethod
    def _move_image(label, ind):
        """
        Moves a file to a new label folder using the shutil library. The file will be moved into a
        subdirectory called label in the input folder. This is an alternative to _copy_image, which is not
        yet used, function would need to be replaced above.
        :param input_path: Path of the original image
        :param label: The label
        """
        root, file_name = os.path.split(df.sorted_in_folder[ind])
        # two lines below check if the filepath contains as an ending a folder with the name of one of the labels
        # if so, this folder is being cut out of the path
        if os.path.split(root)[1] in labels:
            root = os.path.split(root)[0]
        output_path = os.path.join(root, label, file_name)
        print("file_name =",file_name)
        print(" %s --> %s" % (file_name, label))
        move(df.sorted_in_folder[ind], output_path)
            
        # keep track that the image location has been changed by putting the new location-path in sorted_in_folder    
        df.loc[ind,'sorted_in_folder'] = output_path
        #####


def make_folder(directory):
    """
    Make folder if it doesn't already exist
    :param directory: The folder destination path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

# The main bit of the script only gets exectured if it is directly called
if __name__ == "__main__":

    # Make folder for the new labels
    for label in labels:
        make_folder(os.path.join(input_folder_pattern, label))

    # Put all image file paths into a list
    paths = []
    for ext in file_extensions:
        paths.extend(glob.glob(os.path.join(input_folder_pattern, ext), recursive = True))

    if copy_or_move == 'copy':
        try:
            df = pd.read_csv(df_path, header=0)
            # Store configuration file values
        except FileNotFoundError:
            df = pd.DataFrame(columns=["im_path", 'sorted_in_folder'])
            df.im_path = paths
            df.sorted_in_folder = paths
    if copy_or_move == 'move':
        df = pd.DataFrame(columns=["im_path", 'sorted_in_folder'])
        df.im_path = paths
        df.sorted_in_folder = paths
    #######
    
# Start the GUI
root = tk.Tk()
root.title("Happy Labeling :D")
app = ImageGui(root, labels, paths)
root.mainloop()

