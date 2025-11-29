import face_recognition
import numpy as np
import json
from pathlib import Path
import cv2
from typing import Dict, List, Tuple

class FaceRecognizer:
    """
    High-accuracy face recognition system using face_recognition library
    """

    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.encodings_file = self.models_dir / "encodings.json"
        self.known_face_encodings = []
        self.known_face_names = []
        self.encoding_list = {}  # For storing additional metadata

        # Tolerance for face matching (lower = more strict)
        # 0.6 is default, 0.5 is high accuracy
        self.tolerance = 0.5

    def load_encodings(self):
        """Load pre-trained face encodings from file"""
        if self.encodings_file.exists():
            try:
                with open(self.encodings_file, 'r') as f:
                    data = json.load(f)
                    self.encoding_list = data
                    self._rebuild_encoding_lists()
                    print(f"Loaded {len(self.known_face_names)} encodings from file")
            except Exception as e:
                print(f"Error loading encodings: {e}")
        else:
            print("No encodings file found. Train the model first.")

    def _rebuild_encoding_lists(self):
        """Rebuild numpy arrays from stored encodings"""
        self.known_face_encodings = []
        self.known_face_names = []

        for name, encodings_list in self.encoding_list.items():
            for encoding in encodings_list:
                self.known_face_encodings.append(np.array(encoding))
                self.known_face_names.append(name)

    def save_encodings(self):
        """Save encodings to JSON file"""
        try:
            encodings_to_save = {}
            for name, encoding in zip(self.known_face_names, self.known_face_encodings):
                if name not in encodings_to_save:
                    encodings_to_save[name] = []
                encodings_to_save[name].append(encoding.tolist())

            with open(self.encodings_file, 'w') as f:
                json.dump(encodings_to_save, f)
            print(f"Saved {len(self.known_face_names)} encodings to file")
        except Exception as e:
            print(f"Error saving encodings: {e}")

    def train_from_directory(self, data_dir: str) -> int:
        """
        Train the model by encoding all faces in the directory structure.
        Directory structure: data/{person_name}/{image_files.jpg}

        Args:
            data_dir: Path to data directory

        Returns:
            Number of faces trained
        """
        self.known_face_encodings = []
        self.known_face_names = []
        self.encoding_list = {}

        data_path = Path(data_dir)
        total_faces = 0

        if not data_path.exists():
            print(f"Data directory {data_dir} does not exist")
            return 0

        # Iterate through each person directory
        for person_dir in sorted(data_path.iterdir()):
            if not person_dir.is_dir():
                continue

            person_name = person_dir.name
            print(f"Training for {person_name}...")

            person_encodings = []
            image_count = 0

            # Process each image for this person
            for image_path in person_dir.glob("*.jpg"):
                try:
                    # Load image
                    image = face_recognition.load_image_file(str(image_path))

                    # Get face locations and encodings
                    face_locations = face_recognition.face_locations(image, model="hog")
                    face_encodings = face_recognition.face_encodings(
                        image,
                        face_locations,
                        num_jitters=2  # Increased for higher accuracy
                    )

                    # Store encodings
                    for face_encoding in face_encodings:
                        self.known_face_encodings.append(face_encoding)
                        self.known_face_names.append(person_name)
                        person_encodings.append(face_encoding.tolist())
                        total_faces += 1
                        image_count += 1

                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

            if person_encodings:
                self.encoding_list[person_name] = person_encodings
                print(f"  - Trained {image_count} faces for {person_name}")

        # Save encodings
        self.save_encodings()
        print(f"Training complete! Total faces trained: {total_faces}")

        return total_faces

    def recognize_face(self, face_encoding: np.ndarray, confidence_threshold: float = 0.5) -> Dict:
        """
        Recognize a single face encoding.
        High accuracy using strict tolerance.

        Args:
            face_encoding: 128-d face encoding vector
            confidence_threshold: Minimum confidence for match (0-1, higher = stricter)

        Returns:
            Dict with matched status, name, and confidence
        """
        if len(self.known_face_encodings) == 0:
            return {
                "matched": False,
                "name": "Unknown",
                "confidence": 0.0,
                "message": "No trained faces in the system"
            }

        # Compare face to known faces
        face_distances = face_recognition.face_distance(
            self.known_face_encodings,
            face_encoding
        )

        # Find the best match
        best_match_index = np.argmin(face_distances)
        best_match_distance = face_distances[best_match_index]

        # Check if match is within tolerance
        # Lower distance = better match
        # tolerance of 0.5 means distance < 0.5
        if best_match_distance < self.tolerance:
            confidence = 1 - (best_match_distance / self.tolerance)
            name = self.known_face_names[best_match_index]
            return {
                "matched": True,
                "name": name,
                "confidence": float(confidence),
                "distance": float(best_match_distance)
            }
        else:
            confidence = 1 - (best_match_distance / self.tolerance) if best_match_distance < 1.0 else 0.0
            return {
                "matched": False,
                "name": "Unknown",
                "confidence": max(0, float(confidence)),
                "distance": float(best_match_distance)
            }

    def recognize_multiple_faces(self, image: np.ndarray) -> List[Dict]:
        """
        Recognize multiple faces in an image.

        Args:
            image: OpenCV image array

        Returns:
            List of recognition results for each detected face
        """
        face_locations = face_recognition.face_locations(image, model="hog")
        face_encodings = face_recognition.face_encodings(image, face_locations, num_jitters=2)

        results = []
        for face_location, face_encoding in zip(face_locations, face_encodings):
            recognition = self.recognize_face(face_encoding)
            results.append({
                "location": {
                    "top": face_location[0],
                    "right": face_location[1],
                    "bottom": face_location[2],
                    "left": face_location[3]
                },
                **recognition
            })

        return results

    def get_encoding_count(self) -> Dict[str, int]:
        """Get count of encodings per person"""
        return {name: len(encodings) for name, encodings in self.encoding_list.items()}


def encode_face(image_path: str) -> np.ndarray:
    """
    Encode a single face image with high accuracy settings.

    Args:
        image_path: Path to image file

    Returns:
        Face encoding (128-d vector)
    """
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image, model="hog")

    if not face_locations:
        return None

    # Use first detected face
    face_encoding = face_recognition.face_encodings(
        image,
        [face_locations[0]],
        num_jitters=2  # More jitters for better accuracy
    )

    return face_encoding[0] if face_encoding else None


def get_face_encodings(image_path: str) -> List[np.ndarray]:
    """
    Get all face encodings in an image.

    Args:
        image_path: Path to image file

    Returns:
        List of face encodings
    """
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image, model="hog")

    face_encodings = face_recognition.face_encodings(
        image,
        face_locations,
        num_jitters=2
    )

    return face_encodings
