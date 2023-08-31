import cv2, numpy as np, random, string, time, os

def calculate_frame_score(frame):
    # Calculate a score for the frame based on its visual characteristics.
    # You can use metrics like sharpness, brightness, colorfulness, etc.
    # Here's a simple example using brightness as the score.
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    score = np.mean(gray_frame)
    return score

def get_best_thumbnail(video_stream):
    temp_video_path = './temporary/video/file.mp4'  # Replace with an appropriate path

    # Read the video data from the BytesIO object
    video_data = video_stream.read()

    # Write the video data to the temporary file
    with open(temp_video_path, 'wb') as temp_video_file:
        temp_video_file.write(video_data)

    # Now you can use the temporary video file path with cv2.VideoCapture()
    cap = cv2.VideoCapture(temp_video_path)
 
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    best_thumbnail_idx = -1
    best_frame_score = float('-inf')

    for idx in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break

        frame_score = calculate_frame_score(frame)

        if frame_score > best_frame_score:
            best_frame_score = frame_score
            best_thumbnail_idx = idx

    cap.release()

    # Extract and save the best thumbnail
    cap = cv2.VideoCapture(temp_video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, best_thumbnail_idx)
    ret, best_thumbnail = cap.read()
    
    timestamp = int(time.time())
    random_string = ''.join(random.choices(string.ascii_letters, k=6))
    unique_filename = f"{timestamp}_{random_string}_vid_org.jpg"
    
    path = f"./media/gallery/cec/images/{unique_filename}"
    
    if ret:
        cv2.imwrite(path, best_thumbnail)
        print(f"Best thumbnail saved as {unique_filename}")
    else:
        print("Error extracting the best thumbnail.")
        
    cap.release()
    
    os.remove(temp_video_path)

get_best_thumbnail('video2.mp4')