import cv2 as cv
import mediapipe as mp
import pyautogui
import pandas as pd  # Cambié a 'pd' para el alias de pandas, que es el estándar
from pynput.mouse import Controller
import time
import numpy as np
from scipy.spatial import distance



# Función para mostrar pantalla de carga
def show_loading_screen():
    loading_window = cv.namedWindow("Cargando", cv.WINDOW_NORMAL)
    cv.resizeWindow("Cargando", 600, 200)
    
    for i in range(101):
        # Crear imagen negra
        loading_img = np.zeros((200, 600, 3), dtype=np.uint8)
        
        # Dibujar barra de progreso
        cv.rectangle(loading_img, (50, 80), (550, 120), (255, 255, 255), 2)
        cv.rectangle(loading_img, (50, 80), (50 + int(5 * i), 120), (0, 255, 0), -1)
        
        # Texto de porcentaje
        cv.putText(loading_img, f"{i}%", (260, 170), cv.FONT_HERSHEY_SIMPLEX, 
                   0.7, (255, 255, 255), 2)
        
        # Texto de estado
        status_text = "Inicializando componentes..." if i < 33 else \
                     "Cargando modelos de IA..." if i < 66 else \
                     "Iniciando camara..."
        cv.putText(loading_img, status_text, (50, 40), cv.FONT_HERSHEY_SIMPLEX, 
                   0.6, (200, 200, 200), 1)
        
        cv.imshow("Cargando", loading_img)
        cv.waitKey(20)
    
    time.sleep(0.5)
    cv.destroyWindow("Cargando")

# Resto del código anterior (sin cambios en las demás funciones)
# ---------------------------------------------------------------
# [Aquí irían todas las demás funciones y código previo sin modificaciones]
# ---------------------------------------------------------------

# Iniciar pantalla de carga
show_loading_screen()
# Inicializar el controlador del mouse
mouse = Controller()
screen_width, screen_height = pyautogui.size()

# Obtener la posición actual del mouse
cord_x, cord_y = pyautogui.position()
print(cord_x)
print(cord_y)
print(screen_width, "=", screen_height)

# Mover el mouse a una posición inicial
pyautogui.moveTo(658, 363)

# Factor para aumentar la velocidad de movimiento del mouse
speed_factor = 2.0
factor_x = -1  # Ajusta este valor según la calibración

# Inicialización de MediaPipe para detección de manos
mp_hands = mp.solutions.hands
hand_processor = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
# Configuración de suavizado
SMOOTHING_FACTOR = 0.7
prev_x, prev_y = 0, 0
hands = mp_hands.Hands()

# Índices de las puntas de los dedos en MediaPipe
tipIds = [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP,
          mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP,
          mp_hands.HandLandmark.PINKY_TIP]

# Función para detectar si el puño está cerrado
def is_fist_closed(processed):
    if processed.multi_hand_landmarks:
        hand_landmarks = processed.multi_hand_landmarks[0]

        # Obtener la posición de la punta de cada dedo
        finger_tips = [
            mp_hands.HandLandmark.THUMB_TIP,
            mp_hands.HandLandmark.INDEX_FINGER_TIP,
            mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            mp_hands.HandLandmark.RING_FINGER_TIP,
            mp_hands.HandLandmark.PINKY_TIP,
        ]

        closed_fingers = 0
        for tip in finger_tips:
            if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[tip - 2].y:
                closed_fingers += 1

        # Si los 4 dedos (excepto el pulgar) están doblados, la mano está cerrada
        return closed_fingers == 4

    return False

# Función para detectar si los dedos están extendidos
def detect_fingers(landmarks):
    fingers = []

    # Detección para el pulgar (comparando las coordenadas X)
    if landmarks[tipIds[0]].x > landmarks[mp_hands.HandLandmark.THUMB_IP].x:  # THUMB_IP es la articulación intermedia
        fingers.append(1)  # Pulgar extendido
    else:
        fingers.append(0)  # Pulgar doblado

    # Detección para los otros dedos (comparando las coordenadas Y)
    for id in range(1, 5):  # Índice, medio, anular, meñique
        if landmarks[tipIds[id]].y < landmarks[tipIds[id] - 2].y:
            fingers.append(1)  # Dedo extendido
        else:
            fingers.append(0)  # Dedo doblado

    return fingers

data = []

# Función para mover el cursor del mouse
def move_mouse(index_finger_tip):
    if index_finger_tip:
        x = int(index_finger_tip.x * screen_width)
        y = int(index_finger_tip.y * screen_height)
        print("x donde está mi Mano:", x)
        print("y donde está mi Mano:", y)

        # Mover el cursor usando PyAutoGUI
        pyautogui.moveTo(x * speed_factor, y)

        # Guardar las coordenadas en la lista de datos para exportar luego
        data.append({'x': x, 'y': y})

# Función para verificar si la mano está cerrada y realizar la acción de clic
def check_fist_closed(hands_detected, is_holding):
    fist_closed = is_fist_closed(hands_detected)

    if fist_closed and not is_holding:
        pyautogui.mouseDown()
        is_holding = True
        print("Sosteniendo")

    elif not fist_closed and is_holding:
        pyautogui.mouseUp()
        is_holding = False
        print("Soltando")

    return is_holding

# Función para detectar acciones basadas en los dedos
def detect_finger_actions(hands_detected):
    if hands_detected.multi_hand_landmarks:
        for hand_landmarks in hands_detected.multi_hand_landmarks:
            fingers_status = detect_fingers(hand_landmarks.landmark)

            # Clic si el pulgar está doblado y el índice extendido
            if fingers_status[0] == 0 and fingers_status[1] == 1:
                pyautogui.click()
                print("Click")

def detect_finger_actions1(hands_detected):
    if hands_detected.multi_hand_landmarks:
        for hand_landmarks in hands_detected.multi_hand_landmarks:
            fingers_status = detect_fingers(hand_landmarks.landmark)

            # Clic si el pulgar está doblado y el índice extendido
            if fingers_status[4] == 0 and fingers_status[1] == 1:  # Meñique extendido
                pyautogui.rightClick()
                print("Click Derecho")


# Función para mover el cursor según la posición del dedo índice
def move_cursor(hands_detected):
    if hands_detected.multi_hand_landmarks:
        for hand_landmarks in hands_detected.multi_hand_landmarks:
            move_mouse(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP])

is_holding = False

# Abrir la cámara
try:
    cam = cv.VideoCapture(0)
    while cam.isOpened():
        success, frame = cam.read()

        if not success:
            print("Camera Frame not available")
            continue

        # Invertir el fotograma horizontalmente (efecto espejo)
        frame = cv.flip(frame, 1)

        # Convertir el fotograma de BGR a RGB (requerido por MediaPipe)
        frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        # Procesar el fotograma para la detección de manos
        hands_detected = hands.process(frame_rgb)

        # Verificar si la mano está cerrada y actualizar el estado de sostener
        is_holding = check_fist_closed(hands_detected, is_holding)

        # Detectar acciones basadas en los dedos
        detect_finger_actions(hands_detected)
        detect_finger_actions1(hands_detected)
        # Mover el cursor con el dedo índice
        move_cursor(hands_detected)

        # Dibujar los puntos de referencia y las conexiones en el fotograma
        if hands_detected.multi_hand_landmarks:
            for hand_landmarks in hands_detected.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

        # Mostrar el fotograma procesado
        cv.imshow("Control de Mouse con la Mano", frame)

        # Salir del bucle si se presiona la tecla 'q'
        if cv.waitKey(20) & 0xFF == ord('q') or cv.getWindowProperty("Control de Mouse con la Mano", cv.WND_PROP_VISIBLE) < 1:
            break
except Exception as e:
    print(f"Error: {e}")

# Guardar los datos en un archivo Excel
df = pd.DataFrame(data)
#df.to_excel("P:/recoger.xlsx", sheet_name="x_y_listos", index=False, engine="openpyxl")

# Liberar la cámara y cerrar ventanas
cam.release()
cv.destroyAllWindows()
