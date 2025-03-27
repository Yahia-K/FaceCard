import json
import cv2
import numpy as np
import tensorflow as tf
from django.core.exceptions import ObjectDoesNotExist
from .models import Student, FaceEmbedding
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import kagglehub
import logging


model_path = r"C:\Users\ammara\.cache\kagglehub\models\faiqueali\facenet-tensorflow\tensorFlow2\default\2"
model = tf.saved_model.load(model_path)

logger = logging.getLogger(__name__)

def capture_face():

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # we r using direct show backend

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    print("Press 's' to capture an image, or 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            cap.release()
            return None

        cv2.imshow("Capture Face", frame)
        key = cv2.waitKey(1) & 0xFF  # lowering responsiveness wait time

        if key == ord('s'):
            print("Image captured!")
            cap.release()
            cv2.destroyAllWindows()
            return frame

        elif key == ord('q'):
            print("Exiting without capturing.")
            cap.release()
            cv2.destroyAllWindows()
            return None

def process_image(img):
    """preps image for FaceNet processing"""
    img = cv2.resize(img, (160, 160))
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    return tf.convert_to_tensor(img, dtype=tf.float32)

def generate_face_embedding(img):
    """generates face embedding from an image and ensures correct shape"""
    processed_img = process_image(img)
    embedding = model(processed_img)

    embedding_array = embedding.numpy()

    # embedding is (1,128) shape
    if embedding_array.shape[-1] != 128:
        logger.error(f"Unexpected embedding shape: {embedding_array.shape}. Expected (1, 128).")
        return None

    return embedding_array.flatten().tolist()  # convert to list

def save_face_embedding(student_id):
    """captures and stores face embedding for student"""
    try:
        logger.info(f"Fetching student with ID: {student_id}")
        student = Student.objects.get(id=student_id)

        image = capture_face()

        if image is None:
            logger.error("No image captured. Aborting face embedding.")
            return False

        embedding = generate_face_embedding(image)

        if embedding is None:
            logger.error("Failed to generate face embedding. Aborting.")
            return False

        face_embedding, created = FaceEmbedding.objects.get_or_create(student=student)
        face_embedding.embedding = json.dumps(embedding)
        face_embedding.save()

        logger.info(f"Face embedding successfully saved for {student.full_name}.")
        return True

    except ObjectDoesNotExist:
        logger.error(f"Student with ID {student_id} not found.")
        return False

    except Exception as e:
        logger.exception(f"Unexpected error in save_face_embedding: {e}")
        return False

def recognize_face():
    """captures a face and matches it with stored embeddings"""
    image = capture_face()

    if image is None:
        return None, "No face detected."

    captured_embedding = generate_face_embedding(image)

    if captured_embedding is None:
        return None, "Failed to generate face embedding."

    captured_embedding = np.array(captured_embedding)

    all_embeddings = FaceEmbedding.objects.all()

    # compare captured embedding with stored ones
    best_match = None
    min_distance = float("inf")

    for embedding in all_embeddings:
        stored_embedding = np.array(json.loads(embedding.embedding))

        # ensure stored embedding has correct shape
        if stored_embedding.shape != (128,):
            logger.error(f"Invalid stored embedding shape: {stored_embedding.shape}, expected (128,)")
            continue

        # calc distance between embeddings (Euclidean distance)
        distance = np.linalg.norm(captured_embedding - stored_embedding)

        logger.info(f"Comparing with {embedding.student.full_name}, Distance: {distance}")

        if distance < min_distance:  # find closest match
            min_distance = distance
            best_match = embedding.student

    if best_match and min_distance < 10.0:  # threshold
        logger.info(f" Match found: {best_match.full_name}, Distance: {min_distance}")
        return best_match, None
    else:
        logger.info(" No match found.")
        return None, "No match found."
