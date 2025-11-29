from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import face_recognition
import os
import json
import pickle
from pathlib import Path
from datetime import datetime
import asyncio
import base64
from .utils.face_utils import FaceRecognizer, encode_face, get_face_encodings

app = FastAPI(title="Face Recognition AI")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
CAPTURES_DIR = BASE_DIR / "captures"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
CAPTURES_DIR.mkdir(exist_ok=True)

# Initialize face recognizer
face_recognizer = FaceRecognizer(str(MODELS_DIR))

@app.on_event("startup")
async def startup_event():
    """Load encodings on startup"""
    face_recognizer.load_encodings()
    print("Face Recognition system initialized")

@app.get("/")
async def get_html():
    """Serve the main HTML interface"""
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if html_path.exists():
        return FileResponse(html_path, media_type="text/html")
    return HTMLResponse("<h1>Face Recognition AI</h1>")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "system": "Face Recognition AI"}

@app.websocket("/ws/video")
async def websocket_video(websocket: WebSocket):
    """WebSocket endpoint for live video streaming"""
    await websocket.accept()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        await websocket.send_text("error:Camera not available")
        await websocket.close()
        return

    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_data = base64.b64encode(buffer).decode()

            await websocket.send_text(f"frame:{frame_data}")
            await asyncio.sleep(0.03)  # ~30 FPS
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        cap.release()
        await websocket.close()

@app.websocket("/ws/capture")
async def websocket_capture(websocket: WebSocket):
    """WebSocket endpoint for face capture with detection"""
    await websocket.accept()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        await websocket.send_text("error:Camera not available")
        await websocket.close()
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detect faces
            face_locations = face_recognition.face_locations(frame, model="hog")

            # Draw rectangles around faces
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_data = base64.b64encode(buffer).decode()

            response = f"frame:{frame_data}|faces:{len(face_locations)}"
            await websocket.send_text(response)
            await asyncio.sleep(0.03)
    except Exception as e:
        print(f"WebSocket capture error: {e}")
    finally:
        cap.release()
        await websocket.close()

@app.websocket("/ws/recognize")
async def websocket_recognize(websocket: WebSocket):
    """WebSocket endpoint for real-time face recognition"""
    await websocket.accept()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        await websocket.send_text("error:Camera not available")
        await websocket.close()
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    try:
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            matches = []
            names = []

            # Process every other frame for performance
            if frame_count % 2 == 0:
                # Detect faces
                face_locations = face_recognition.face_locations(frame, model="hog")
                face_encodings = face_recognition.face_encodings(frame, face_locations)

                # Recognize faces
                for face_encoding in face_encodings:
                    match = face_recognizer.recognize_face(face_encoding)
                    matches.append(match["matched"])
                    names.append(match["name"])
            else:
                face_locations = face_recognition.face_locations(frame, model="hog")

            # Draw results
            for (top, right, bottom, left), match_found, name in zip(face_locations, matches, names):
                color = (0, 255, 0) if match_found else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                if match_found:
                    cv2.putText(frame, name, (left, top - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                else:
                    cv2.putText(frame, "Unknown", (left, top - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_data = base64.b64encode(buffer).decode()

            response = f"frame:{frame_data}|detected:{len(face_locations)}"
            await websocket.send_text(response)
            await asyncio.sleep(0.03)
    except Exception as e:
        print(f"WebSocket recognize error: {e}")
    finally:
        cap.release()
        await websocket.close()

@app.websocket("/ws/auto-capture")
async def websocket_auto_capture(websocket: WebSocket):
    """WebSocket endpoint for automatic face capture for training"""
    await websocket.accept()

    # Receive person name from client
    try:
        data = await websocket.receive_text()
        person_name = data.strip()
    except Exception as e:
        await websocket.send_text(f"error:Failed to receive person name: {str(e)}")
        await websocket.close()
        return

    # Create person directory
    person_dir = DATA_DIR / person_name
    person_dir.mkdir(exist_ok=True)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        await websocket.send_text("error:Camera not available")
        await websocket.close()
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    try:
        captured_count = 0
        frame_count = 0
        last_capture_time = {}  # Track last capture time for each face to avoid duplicates

        await websocket.send_text("status:Ready. Position your face in front of the camera.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Detect faces
            face_locations = face_recognition.face_locations(frame, model="hog")
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            # Draw rectangles and capture
            for idx, (top, right, bottom, left) in enumerate(face_locations):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # Generate unique key for this face position
                face_key = f"{left}_{top}_{right}_{bottom}"
                current_time = datetime.now()

                # Capture frames automatically - one every 0.5 seconds per face
                if face_key not in last_capture_time or \
                   (current_time - last_capture_time[face_key]).total_seconds() > 0.5:

                    # Save the frame
                    timestamp = current_time.strftime("%Y%m%d_%H%M%S%f")[:-3]
                    filename = f"{person_name}_{timestamp}.jpg"
                    filepath = person_dir / filename

                    cv2.imwrite(str(filepath), frame)
                    captured_count += 1
                    last_capture_time[face_key] = current_time

                    # Send update to client
                    await websocket.send_text(
                        f"captured:{captured_count}|detected:{len(face_locations)}|"
                        f"filename:{filename}"
                    )

            # If no faces detected, send status
            if len(face_locations) == 0:
                await websocket.send_text(
                    f"status:No face detected. Total captured: {captured_count}"
                )
            else:
                # Send frame for preview
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_data = base64.b64encode(buffer).decode()
                await websocket.send_text(
                    f"frame:{frame_data}|captured:{captured_count}"
                )

            await asyncio.sleep(0.03)

    except Exception as e:
        await websocket.send_text(f"error:Capture error: {str(e)}")
    finally:
        cap.release()
        await websocket.send_text(
            f"complete:Captured {captured_count} frames for {person_name}"
        )
        await websocket.close()

@app.post("/api/capture-face")
async def capture_face(name: str, file: UploadFile = File(...)):
    """Capture and store a face image"""
    try:
        # Create person directory
        person_dir = DATA_DIR / name
        person_dir.mkdir(exist_ok=True)

        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        # Check if face is detected
        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            raise HTTPException(status_code=400, detail="No face detected in image")

        # Save image with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.jpg"
        filepath = person_dir / filename

        cv2.imwrite(str(filepath), image)

        return {
            "success": True,
            "message": f"Face captured for {name}",
            "filename": filename,
            "faces_detected": len(face_locations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/train")
async def train_model():
    """Train the face recognition model"""
    try:
        trained_count = face_recognizer.train_from_directory(str(DATA_DIR))
        return {
            "success": True,
            "message": "Model trained successfully",
            "faces_trained": trained_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/people")
async def get_people():
    """Get list of all people with captured faces"""
    try:
        people = []
        if DATA_DIR.exists():
            for person_dir in DATA_DIR.iterdir():
                if person_dir.is_dir():
                    face_count = len(list(person_dir.glob("*.jpg")))
                    people.append({
                        "name": person_dir.name,
                        "face_count": face_count
                    })
        return {"people": people}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/people/{name}")
async def delete_person(name: str):
    """Delete all faces for a person"""
    try:
        person_dir = DATA_DIR / name
        if person_dir.exists():
            import shutil
            shutil.rmtree(person_dir)
            face_recognizer.train_from_directory(str(DATA_DIR))
            return {"success": True, "message": f"Deleted all faces for {name}"}
        raise HTTPException(status_code=404, detail=f"Person {name} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    try:
        people = []
        total_faces = 0

        if DATA_DIR.exists():
            for person_dir in DATA_DIR.iterdir():
                if person_dir.is_dir():
                    face_count = len(list(person_dir.glob("*.jpg")))
                    people.append({
                        "name": person_dir.name,
                        "face_count": face_count
                    })
                    total_faces += face_count

        return {
            "total_people": len(people),
            "total_faces": total_faces,
            "people": people
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
