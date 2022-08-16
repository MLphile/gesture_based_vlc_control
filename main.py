from model_architecture import model
import pandas as pd
import mediapipe as mp
from utils import *


# Camera resolution
width = 1280//2
height = 720//2


# Camera setting
cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)


# Screen size
screen_size = pyautogui.size()


# Hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75)

# Hand landmarks drawing
mp_drawing = mp.solutions.drawing_utils

# Load model
model.load_state_dict(torch.load('model.pth'))

# Load Label
labels = pd.read_csv('data/label.csv', header=None).values.flatten().tolist()

mode = 0  # mode normal by default

while True:

    key = cv.waitKey(1)
    if key == ord('q'):
        break

    # reset mode and class id
    class_id, mode = select_mode(key, mode)

    # read camera
    has_frame, frame = cap.read()
    if not has_frame:
        break

    # horizontal flip and color conversion for mediapipe
    frame = cv.flip(frame, 1)
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    # landmarks detection
    results = hands.process(frame_rgb)

    # if detection
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            # draw landmarks
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # get landmarks coordinates
            coordinates_list = calc_landmark_coordinates(frame, hand_landmarks)

            # Conversion to relative coordinates and normalized coordinates
            preprocessed = pre_process_landmark(
                coordinates_list)

            # inference
            # pred = predict(preprocessed, model)
            # command = labels[pred]

            # activate/deactivate mouse_mode
            mouse_mode = True
            x, y = frame_to_screen(coordinates_list[6], frame.shape[:2], screen_size)
            move_mouse(x, y, mouse_mode)
            # print('wrist:', coordinates_list[0]) 
            
            # keyboard

            # mouse

            

            # cv.putText(frame, f'COMMAND: {command}', (int(width*0.05), int(height*0.1)),
            #            cv.FONT_HERSHEY_COMPLEX, 1, (22, 69, 22), 3, cv.LINE_AA)

            # Write to the dataset file (if mode == 1)
            logging_csv(class_id, mode, preprocessed)

        


    frame = draw_info(frame, mode, class_id)
    cv.imshow('', frame)


cap.release()
cv.destroyAllWindows()
