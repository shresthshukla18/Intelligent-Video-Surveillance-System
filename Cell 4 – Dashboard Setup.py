# cell 4

code = r"""
import streamlit as st
import os
import subprocess
import pandas as pd
import json
import time
import matplotlib.pyplot as plt
from pipeline import run_pipeline

BASE_PATH = "/content/drive/MyDrive/cv_project"

VIDEO_FOLDER = f"{BASE_PATH}/videos"
UPLOAD_FOLDER = f"{BASE_PATH}/uploads"
OUTPUT_FOLDER = f"{BASE_PATH}/output"

os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

MAX_UPLOADS = 10
MAX_RUNS = 10

def cleanup_folder(folder_path, max_items):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
    if len(files) <= max_items:
        return
    files.sort(key=os.path.getctime)
    while len(files) > max_items:
        oldest = files.pop(0)
        if os.path.isfile(oldest):
            os.remove(oldest)
        else:
            import shutil
            shutil.rmtree(oldest)

def convert_to_web_video(input_path):
    output_path = input_path.replace(".mp4", "_web.mp4")
    if not os.path.exists(output_path):
        subprocess.run([
            "ffmpeg","-y","-i", input_path,
            "-vcodec","libx264","-acodec","aac",
            output_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

st.title("Intelligent Video Surveillance Dashboard")

cleanup_folder(UPLOAD_FOLDER, MAX_UPLOADS)
cleanup_folder(OUTPUT_FOLDER, MAX_RUNS)

if "result" not in st.session_state:
    st.session_state.result = None

# ================= UPLOAD =================
st.subheader("Upload Your Own Video")

uploaded_file = st.file_uploader("Upload Video", type=["mp4","avi","mov"])

if uploaded_file is not None:
    file_size_mb = len(uploaded_file.getvalue())/(1024*1024)

    if file_size_mb > 200:
        st.error("File too large (max 200MB)")
    else:
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in [".mp4",".avi",".mov"]:
            st.error("Invalid format")
        else:
            timestamp = int(time.time())
            unique_name = f"{timestamp}_{uploaded_file.name}"
            save_path = os.path.join(UPLOAD_FOLDER, unique_name)

            with open(save_path,"wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success("Uploaded successfully")

            if st.button("Run Uploaded Video"):
                st.write("Processing uploaded video...")
                st.session_state.result = run_pipeline(save_path)
                st.success("Done")

# ================= SAMPLE =================
videos = [
    v for v in os.listdir(VIDEO_FOLDER)
    if v.endswith((".mp4",".avi",".mov")) and not v.endswith("_web.mp4")
]

if len(videos) == 0:
    st.warning("No sample videos found.")
else:
    st.subheader("Run Sample Video")
    selected = st.selectbox("Select Sample Video", videos)

    if st.button("Run Sample Video"):
        video_path = os.path.join(VIDEO_FOLDER, selected)
        st.write("Processing...")
        st.session_state.result = run_pipeline(video_path)
        st.success("Done")

# ================= OUTPUT =================
if st.session_state.result:

    result = st.session_state.result

    st.subheader("Summary")
    st.write(result["summary"])

    st.info(
"The summary represents the overall behavior of the video from the first frame to the last frame.\n\n"

f"Total Tracks Created ({result['summary']['tracks_created']}) indicates how many unique object tracks were initialized during the video. "
"This happens when a new object is detected consistently for a few frames and assigned a stable ID.\n\n"

f"Total Tracks Lost ({result['summary']['tracks_lost']}) represents how many of those tracked objects disappeared due to occlusion or exiting the scene. "
"A gap between created and lost tracks suggests how many objects were still active at the end.\n\n"

f"Peak Occupancy ({result['summary']['peak_occupancy']}) is the maximum number of objects visible in a single frame, "
"showing the highest crowd density moment in the video.\n\n"

"Direction flow represents movement trends across the entire video. "
"It is calculated by comparing the position of each tracked object between consecutive frames.\n\n"

f"Left to Right ({result['summary']['direction_flow']['left_to_right']}) means the object moved horizontally towards the right, "
f"while Right to Left ({result['summary']['direction_flow']['right_to_left']}) indicates movement towards the left.\n\n"

f"Top to Bottom ({result['summary']['direction_flow']['top_to_bottom']}) shows downward movement, "
f"and Bottom to Top ({result['summary']['direction_flow']['bottom_to_top']}) shows upward movement.\n\n"

"These values are accumulated frame by frame, meaning every small movement contributes to the total count. "
"So higher values indicate dominant movement patterns rather than number of unique objects.\n\n"

f"Average FPS ({result['summary']['avg_fps']}) represents the processing speed of the system, "
"showing how many frames are processed per second on average."
)

    st.subheader("Annotated Video")
    st.video(convert_to_web_video(result["video"]))

    st.info(
"This annotated video shows real-time object detection and tracking results. "
"Each bounding box represents a detected object, and the number displayed is its assigned track ID.\n\n"

"The ID remains consistent as long as the object is continuously tracked. "
"If tracking is interrupted, the object may receive a new ID when detected again.\n\n"

"This visualization helps understand how the system detects, tracks, and differentiates multiple objects in the scene."
)

    st.subheader("Heatmap Video")
    st.video(convert_to_web_video(result["heatmap_video"]))

    st.info(
"The heatmap video visualizes movement intensity across the scene. "
"Areas with higher activity appear in warmer colors such as red and yellow, "
"while less active regions appear in cooler colors like blue.\n\n"

"This is generated by accumulating object positions over time, "
"highlighting frequently visited zones and movement patterns.\n\n"

"It helps identify crowded areas and common movement paths in the video."
)

    st.subheader("Overlay Video")
    st.video(convert_to_web_video(result["overlay"]))

    st.info(
"The overlay video combines both tracking and heatmap information. "
"It shows detected objects along with their movement intensity in a single view.\n\n"

"This allows simultaneous observation of object tracking and crowd behavior, "
"making it easier to analyze both individual movement and overall activity."
)

    st.subheader("Heatmap Image")
    st.image(result["heatmap_img"])

    st.subheader("Download Performance CSV")
    with open(result["csv"], "rb") as file:
        st.download_button("Download CSV", file.read(),
            os.path.basename(result["csv"]), "text/csv")

    st.subheader("CSV Preview")
    df = pd.read_csv(result["csv"])
    st.dataframe(df.head(100))

    st.info(
"The CSV file contains frame-by-frame analytics generated during processing. "
"Each row represents a single frame, and the values are cumulative over time.\n\n"

"It includes metrics such as FPS, occupancy, tracks created, tracks lost, "
"entry/exit counts, and speed classifications.\n\n"

"The final row of the CSV corresponds to the summary values shown above, "
"providing a detailed breakdown of how those results were computed."
)

    # =========================================================
    # ===== NEW ANALYTICS SECTION (ADDED ONLY) =================
    # =========================================================

    st.subheader("📊 Crowd Trend Analysis")
    fig1 = plt.figure()
    plt.plot(df["Frame"], df["Occupancy"])
    plt.xlabel("Frame")
    plt.ylabel("Occupancy")
    plt.title("Crowd Density Over Time")
    st.pyplot(fig1)

    st.info(
"This graph shows how the number of active objects (occupancy) changes over time. "
"The x-axis represents frame number, and the y-axis represents the number of tracked objects.\n\n"

"It helps visualize crowd density patterns, including peaks and drops in activity throughout the video."
)

    st.subheader("⚡ Performance Analysis")
    fig2 = plt.figure()
    plt.plot(df["Frame"], df["FPS"])
    plt.xlabel("Frame")
    plt.ylabel("FPS")
    plt.title("FPS Over Time")
    st.pyplot(fig2)

    st.info(
"This graph represents the system's processing speed over time using FPS (frames per second). "
"Higher FPS indicates faster processing, while drops in FPS may occur during complex scenes.\n\n"

"It helps analyze the performance stability of the detection and tracking pipeline."
)

    st.subheader("🔁 Track Behavior Analysis")
    fig3 = plt.figure()
    plt.plot(df["Frame"], df["Tracks_Created"], label="Tracks Created")
    plt.plot(df["Frame"], df["Tracks_Lost"], label="Tracks Lost")
    plt.xlabel("Frame")
    plt.ylabel("Count")
    plt.title("Track Creation & Loss Over Time")
    plt.legend()
    st.pyplot(fig3)

    st.info(
"This graph shows how tracking evolves over time by plotting total tracks created and lost.\n\n"

"Tracks created increase when new objects are detected, while tracks lost increase when objects disappear.\n\n"

"The gap between these values gives an indication of tracking stability and object persistence in the scene."
)

    st.subheader("📉 Tracking Stability")
    created = df["Tracks_Created"].iloc[-1]
    lost = df["Tracks_Lost"].iloc[-1]

    st.write(f"Total Tracks Created: {created}")
    st.write(f"Total Tracks Lost: {lost}")
    st.write(f"Tracking Gap (Instability Indicator): {created - lost}")

    st.info("Track IDs are dynamically assigned by the tracking algorithm (ByteTrack). "
"When an object is detected in a frame, the tracker compares it with previously seen objects "
"based on position and motion. If it matches an existing object, it keeps the same ID. "
"If no match is found, a new ID is generated.\n\n"

"An ID becomes valid only after the object is detected consistently for a few frames, "
"which avoids false detections. This is why track creation is slightly delayed.\n\n"

"As the video progresses frame by frame, each object keeps its ID as long as it is visible. "
"If the object disappears due to occlusion or leaving the scene, the ID is removed and counted as a lost track. "
"If the same object reappears later, it may be assigned a new ID.\n\n"

"The numbers you see on bounding boxes in the video are these track IDs. "
"They are not fixed labels for real-world objects but temporary identifiers assigned during tracking.\n\n"

"In the CSV file, we do not store individual IDs per frame. Instead, we record cumulative statistics "
"such as how many tracks were created and lost over time. These values increase from frame 1 to the last frame, "
"representing how tracking evolves throughout the video.")

    # =========================================================

    st.subheader("Download Outputs")

    with open(result["video"], "rb") as f:
        st.download_button("Download Annotated Video", f.read(),
            os.path.basename(result["video"]), "video/mp4")

    with open(result["heatmap_video"], "rb") as f:
        st.download_button("Download Heatmap Video", f.read(),
            os.path.basename(result["heatmap_video"]), "video/mp4")

    with open(result["overlay"], "rb") as f:
        st.download_button("Download Overlay Video", f.read(),
            os.path.basename(result["overlay"]), "video/mp4")

    with open(result["heatmap_img"], "rb") as f:
        st.download_button("Download Heatmap Image", f.read(),
            os.path.basename(result["heatmap_img"]), "image/png")

    summary_json = json.dumps(result["summary"], indent=4)

    st.download_button("Download Summary (JSON)", summary_json,
        "summary.json", "application/json")
"""

with open("dashboard.py", "w") as f:
    f.write(code)

print("dashboard.py updated safely with analytics section")
