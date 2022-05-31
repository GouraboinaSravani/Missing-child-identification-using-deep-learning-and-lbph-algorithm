import os
import numpy as np
import cv2
import face_recognition
from sklearn.model_selection import check_cv
import G6_iris_recognition as ir

known_faces, known_names = None,None

if "faces" not in list(os.listdir()):
    os.mkdir("faces")


def retrain_completely(KNOWN_FACES_DIR = 'faces', max_image_height = 1000):
    '''
    Call this function to completely Retrain the Model from Starting.
    It will Read all the images in all the folders from "faces" folder.
    It will assign the Folder Name as person name.
    It will also delete all the images in which face is not detected, hence useless for the model.
    '''
    global known_faces, known_names

    print('Loading known faces...')
    known_faces_temp = []
    known_names_temp = []
    for name in os.listdir(KNOWN_FACES_DIR):
        for filename in os.listdir(f"{KNOWN_FACES_DIR}/{name}"):
            
            try:
                image_data = face_recognition.load_image_file(f"{KNOWN_FACES_DIR}/{name}/{filename}")
                print("Training for:", filename)
                encoding = face_recognition.face_encodings(image_data)[0]
                known_faces_temp.append(encoding)
                known_names_temp.append(name)
            except Exception as e:
                print('Face not detected', e)
                os.remove(f"{KNOWN_FACES_DIR}/{name}/{filename}")

    print(known_names)
    np.save('known_faces', np.array(known_faces_temp))
    np.save('known_names', np.array(known_names_temp))

    known_faces, known_names = None,None


def add_face(folder_path, name=None, max_image_height = 1000):
    '''
    Call this folder to add a face to the model.
    It will read all the images inside the given folder path.
    By default it will assign person name as folder name, although you can pass custom name as 2nd arg.
    It will also delete all the images in which face is not detected, hence useless for the model.
    '''
    global known_faces, known_names

    try:
        known_faces_temp = np.load('known_faces.npy', allow_pickle=True).tolist()
        known_names_temp = np.load('known_names.npy', allow_pickle=True).tolist()
    except:
        known_faces_temp = []
        known_names_temp = []

    if name is None:
        name = folder_path.split("/")[-1]

    for filename in os.listdir(folder_path):
        
        try:
            image_data = face_recognition.load_image_file(folder_path + f"/{filename}")
            print("Training for:", filename)
            encoding = face_recognition.face_encodings(image_data)[0]
            known_faces_temp.append(encoding)
            known_names_temp.append(name)
        except Exception as e:
            print('No Face Detected.', e)
            os.remove(folder_path + f"/{filename}")

    print("Training for Folder ", folder_path,"Done.")

    np.save('known_faces', np.array(known_faces_temp))
    np.save('known_names', np.array(known_names_temp))

    known_faces, known_names = None,None

def add_face_gui():
    '''
    Uses Add folder
    Call the folder to directly open File Explorer and select desired folder for adding new face
    '''
    from tkinter import filedialog
    import tkinter
    root = tkinter.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    add_face(folder_selected)


def remove_face(name):
    '''
    Call to remove data about a face using name.
    '''
    global known_faces, known_names

    known_faces_temp = np.load('known_faces.npy', allow_pickle=True).tolist()
    known_names_temp = np.load('known_names.npy', allow_pickle=True).tolist()

    for _ in range(known_names_temp.count(name)):
        face_index = known_names_temp.index(name)
        known_names_temp.pop(face_index)
        known_faces_temp.pop(face_index)

    np.save('known_names', np.array(known_names_temp))
    np.save('known_faces', np.array(known_faces_temp))

    known_faces, known_names = None,None
    

def checkface(raw_image):
    '''
    Pass the raw cv2 image to check face.
    Return a list of lists containing name of detected face and location coordinates of that face.
    max_image_height is used to scale down the image for fater performance.
    '''
    global known_faces, known_names
    MODEL = 'hog'
    TOLERANCE = 0.4

    if known_faces is None:
        print('Loading known faces...', end =" ")
        known_faces = np.load('known_faces.npy', allow_pickle=True).tolist()
        known_names = np.load('known_names.npy', allow_pickle=True).tolist()
        print("Loaded all known Faces")
    image_rgb = raw_image
    locations = face_recognition.face_locations(image_rgb, model=MODEL)
    encodings = face_recognition.face_encodings(image_rgb, locations)
    names_and_locations = []


    for face_encoding, face_location in zip(encodings, locations):
        results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
        if True in results:
            match = known_names[results.index(True)]
            name = match.split(",")[0]
            names_and_locations.append([name, face_location])
        else:
            names_and_locations.append(['Unknown', face_location])
    
    return names_and_locations


def checkface_and_draw(raw_image):
    '''
    Uses checkface function
    Return the image by drawing the faces and names on the image, and also list of all the names detected
    '''

    FRAME_THICKNESS = 3
    FONT_THICKNESS = 2

    names_and_locations = checkface(raw_image)
    name_list = []

    if len(names_and_locations) > 0:
        for name, face_location in names_and_locations:
            name_list.append(name)
            
            #Box for Face
            color = [(ord(c.lower()) - 97) * 8 for c in name[:3]]
            top_left = (face_location[3], face_location[0])
            bottom_right = (face_location[1], face_location[2])
            cv2.rectangle(raw_image, top_left, bottom_right, color, FRAME_THICKNESS)
            
            #Box for Name
            top_left = (face_location[3]-2, face_location[0]-22)
            bottom_right = (face_location[1]+2, face_location[0])
            cv2.rectangle(raw_image, top_left, bottom_right, color, cv2.FILLED)
            cv2.putText(raw_image, name, (face_location[3] + 10, face_location[0] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200,200), FONT_THICKNESS)
    
    return raw_image, name_list

def checkface_folder(foldername):
    op = []
    for file in os.listdir(foldername):
        try:
            image_data = face_recognition.load_image_file(foldername + f"/{file}")
            res = checkface(image_data)
            for i in res:
                op.append(i[0])
        except Exception as e:
            print(e)
    
    return op




