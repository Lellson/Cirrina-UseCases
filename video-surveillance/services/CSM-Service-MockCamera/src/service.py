import base64
import json
import hashlib
import os
import time

import cv2
import uvicorn
import numpy as np
from fastapi import FastAPI, HTTPException, Request, Response
import ContextVariable_pb2
from google.protobuf.json_format import MessageToDict

FPS = 30

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_CAPTURES = {
    0: cv2.VideoCapture(os.path.join(ROOT_DIR, "resources", "1.avi")),
    1: cv2.VideoCapture(os.path.join(ROOT_DIR, "resources", "2.avi")),
    2: cv2.VideoCapture(os.path.join(ROOT_DIR, "resources", "3.avi")),
    3: cv2.VideoCapture(os.path.join(ROOT_DIR, "resources", "4.avi")),
    4: cv2.VideoCapture(os.path.join(ROOT_DIR, "resources", "5.avi")),
}
app = FastAPI()

# Decide whether protobuf should be used (optional environment variable)
proto = "PROTO" not in os.environ \
    or os.environ["PROTO"].lower() in ["true", "t", "1"]

def get_frame_number() -> int:
    return round(int(time.time()) * FPS)


def log_hash(data: bytes, a: float, b: float):
    sha256 = hashlib.sha256()
    sha256.update(data)
    hash = sha256.hexdigest()

    log_entry = f"{hash},{a},{b}\n"

    with open("/tmp/log.csv", "a") as log_file:
        log_file.write(log_entry)


@app.post("/capture")
async def capture(request: Request):
    a = time.time()

    video_number = None
    delay = None

    if proto:
        # Read the raw request body
        body = await request.body()

        # Parse the protobuf message
        context_variables = ContextVariable_pb2.ContextVariables()
        context_variables.ParseFromString(body)

        # Extract specific values
        for context_variable in context_variables.data:
            context_variable_dict = MessageToDict(context_variable)

            # Check for video_number and delay
            if context_variable_dict["name"] == "video_number":
                video_number = context_variable_dict["value"].get("integer")
            elif context_variable_dict["name"] == "delay":
                delay = context_variable_dict["value"].get("integer")
    else:
        # Parse the request variables
        context_variables = await request.json()

        # Get context variables from the request json
        if "video_number" in context_variables:
            video_number = int(context_variables["video_number"])
        if "delay" in context_variables:
            delay = int(context_variables["delay"])

    if video_number not in VIDEOS_CAPTURES:
        raise HTTPException(
            status_code=400, detail=f"Invalid video_number: {video_number}"
        )

    cap = VIDEOS_CAPTURES[video_number]
    video_path = os.path.join(ROOT_DIR, "resources", f"{video_number + 1}.avi")

    if not cap.isOpened():
        print(f"Failed to open video {video_number}")
        raise HTTPException(
            status_code=400, detail=f"Failed to open video {video_number}"
        )

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_number = get_frame_number() % total_frames
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    ret, frame = cap.read()
    if not ret:
        raise HTTPException(status_code=400, detail="Unable to capture frame")

    frame = cv2.resize(frame, (640, 480))

    random_values = (np.random.rand(1, frame.shape[1], frame.shape[2]) * 256).astype(
        np.uint8
    )

    frame[:1, :, :] = random_values

    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), 80]

    _, buffer = cv2.imencode(".jpg", frame, jpeg_params)

    buffer_bytes = buffer.tobytes()

    if proto:
        # Create response protobuf message
        response_context_variables = ContextVariable_pb2.ContextVariables()
        image_context_variable = ContextVariable_pb2.ContextVariable(
            name="camera_image", value=ContextVariable_pb2.Value(bytes=buffer_bytes)
        )
        response_context_variables.data.append(image_context_variable)

        # Serialize the response to protobuf format
        response = response_context_variables.SerializeToString()
        media_type = "application/x-protobuf"
    else:
        buffer_base64 = base64.b64encode(buffer_bytes).decode('utf-8')

        response = json.dumps({
            "camera_image": buffer_base64
        })
        media_type = "application/json"

    b = time.time()

    log_hash(buffer_bytes, a, b)

    # Return the protobuf response
    return Response(content=response, media_type=media_type)


if __name__ == "__main__":
    print(f"Protobuf: {proto}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
