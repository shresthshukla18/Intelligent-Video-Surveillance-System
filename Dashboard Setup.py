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

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Intelligent Video Surveillance", page_icon="👁️", layout="wide")

# --- CUSTOM CSS FOR CLEANER UI ---
st.markdown('''
<style>
    /* Hide default Streamlit menu and footer for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Soften the metric boxes */
    div[data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.1);
        padding: 5% 5% 5% 10%;
        border-radius: 10px;
    }
</style>
''', unsafe_allow_html=True)


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

cleanup_folder(UPLOAD_FOLDER, MAX_UPLOADS)
cleanup_folder(OUTPUT_FOLDER, MAX_RUNS)

if "result" not in st.session_state:
    st.session_state.result = None

# ================= SIDEBAR (INPUTS) =================
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.write("Upload a video or choose a sample to begin processing.")
    st.divider()

    st.subheader("📁 Upload Video")
    uploaded_file = st.file_uploader("Drop video here", type=["mp4","avi","mov"])

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

                if st.button("▶ Run Upload", use_container_width=True, type="primary"):
                    with st.spinner("Processing video pipeline..."):
                        st.session_state.result = run_pipeline(save_path)

    st.divider()

    st.subheader("🎞️ Run Sample")
    videos = [
        v for v in os.listdir(VIDEO_FOLDER)
        if v.endswith((".mp4",".avi",".mov")) and not v.endswith("_web.mp4")
    ]

    if len(videos) == 0:
        st.warning("No sample videos found.")
    else:
        selected = st.selectbox("Select Sample Video", videos, label_visibility="collapsed")
        if st.button("▶ Run Sample", use_container_width=True, type="primary"):
            video_path = os.path.join(VIDEO_FOLDER, selected)
            with st.spinner("Processing sample video..."):
                st.session_state.result = run_pipeline(video_path)


# ================= MAIN DASHBOARD (OUTPUTS) =================
st.title("👁️ Intelligent Video Surveillance")
st.markdown("Automated crowd tracking, movement analysis, and anomaly detection.")

if not st.session_state.result:
    st.info("👈 Please run a video from the sidebar to view analytics.")

if st.session_state.result:
    result = st.session_state.result

    st.divider()

    # --- KPI METRICS ROW ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Peak Occupancy", result['summary']['peak_occupancy'])
    col2.metric("Tracks Created", result['summary']['tracks_created'])
    col3.metric("Tracks Lost", result['summary']['tracks_lost'])
    col4.metric("Average FPS", f"{result['summary']['avg_fps']:.1f}")

    with st.expander("ℹ️ How to interpret these metrics"):
        st.write(
            "**Total Tracks Created** indicates how many unique object tracks were initialized. "
            "**Total Tracks Lost** represents tracked objects that disappeared. "
            "**Peak Occupancy** is the maximum crowd density in a single frame."
        )

    st.write("") # Spacer

    # --- TABS LAYOUT ---
    tab_viz, tab_graphs, tab_data = st.tabs(["🎥 Visualizations", "📈 Trend Analysis", "💾 Data & Export"])

    # 1. VISUALIZATIONS TAB
    with tab_viz:
        st.subheader("Pipeline Outputs")
        vid_col1, vid_col2 = st.columns(2)

        with vid_col1:
            st.markdown("**Annotated Tracking**")
            st.video(convert_to_web_video(result["video"]))
            with st.expander("About Tracking"):
                st.write("Shows real-time detection. Bounding boxes represent objects, and numbers are assigned track IDs. IDs remain consistent unless tracking is interrupted.")

            st.markdown("**Movement Heatmap**")
            st.video(convert_to_web_video(result["heatmap_video"]))
            with st.expander("About Heatmaps"):
                st.write("Visualizes movement intensity. Warmer colors (red/yellow) show high activity, cooler colors (blue) show less active regions.")

        with vid_col2:
            st.markdown("**Overlay Integration**")
            st.video(convert_to_web_video(result["overlay"]))
            with st.expander("About Overlay"):
                st.write("Combines tracking and heatmap information to allow simultaneous observation of individual movement and crowd behavior.")

            st.markdown("**Final Heatmap Summary**")
            st.image(result["heatmap_img"], use_column_width=True)

    # 2. GRAPHS TAB
    with tab_graphs:
        df = pd.read_csv(result["csv"])

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Crowd Density Over Time")
            fig1 = plt.figure(figsize=(6, 4))
            plt.plot(df["Frame"], df["Occupancy"], color="#1f77b4", linewidth=2)
            plt.xlabel("Frame", fontsize=9)
            plt.ylabel("Occupancy", fontsize=9)
            plt.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig1)

            st.subheader("Performance (FPS)")
            fig2 = plt.figure(figsize=(6, 4))
            plt.plot(df["Frame"], df["FPS"], color="#ff7f0e", linewidth=2)
            plt.xlabel("Frame", fontsize=9)
            plt.ylabel("FPS", fontsize=9)
            plt.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig2)

        with col_g2:
            st.subheader("Track Behavior Analysis")
            fig3 = plt.figure(figsize=(6, 4))
            plt.plot(df["Frame"], df["Tracks_Created"], label="Tracks Created", color="#2ca02c", linewidth=2)
            plt.plot(df["Frame"], df["Tracks_Lost"], label="Tracks Lost", color="#d62728", linewidth=2)
            plt.xlabel("Frame", fontsize=9)
            plt.ylabel("Count", fontsize=9)
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig3)

            # Tracking Stability Box
            created = df["Tracks_Created"].iloc[-1]
            lost = df["Tracks_Lost"].iloc[-1]
            st.info(f"**Tracking Gap (Instability Indicator):** {created - lost}\n\n*A larger gap may indicate frequent occlusion or objects lingering in the scene.*")

            with st.expander("ℹ️ Read more about tracking stability"):
                st.write(
                    "Track IDs are dynamically assigned by the tracking algorithm (ByteTrack). "
                    "When an object is detected, the tracker compares it with previously seen objects based on position and motion. "
                    "If tracking fails due to occlusion, the ID is dropped (Lost Track). When found again, a new ID is generated (Created Track)."
                )

    # 3. DATA & EXPORT TAB
    with tab_data:
        st.subheader("Movement Flow Summary")
        flow = result['summary']['direction_flow']
        flow_col1, flow_col2, flow_col3, flow_col4 = st.columns(4)
        flow_col1.metric("Left → Right", flow.get('left_to_right', 0))
        flow_col2.metric("Right → Left", flow.get('right_to_left', 0))
        flow_col3.metric("Top ↓ Bottom", flow.get('top_to_bottom', 0))
        flow_col4.metric("Bottom ↑ Top", flow.get('bottom_to_top', 0))

        st.divider()

        st.subheader("Export Artifacts")
        d_col1, d_col2, d_col3 = st.columns(3)

        with open(result["video"], "rb") as f:
            d_col1.download_button("📥 Annotated Video", f.read(), os.path.basename(result["video"]), "video/mp4", use_container_width=True)

        with open(result["heatmap_video"], "rb") as f:
            d_col2.download_button("📥 Heatmap Video", f.read(), os.path.basename(result["heatmap_video"]), "video/mp4", use_container_width=True)

        with open(result["overlay"], "rb") as f:
            d_col3.download_button("📥 Overlay Video", f.read(), os.path.basename(result["overlay"]), "video/mp4", use_container_width=True)

        d_col4, d_col5, d_col6 = st.columns(3)
        with open(result["heatmap_img"], "rb") as f:
            d_col4.download_button("🖼️ Heatmap Image", f.read(), os.path.basename(result["heatmap_img"]), "image/png", use_container_width=True)

        with open(result["csv"], "rb") as f:
            d_col5.download_button("📊 Raw CSV Data", f.read(), os.path.basename(result["csv"]), "text/csv", use_container_width=True)

        summary_json = json.dumps(result["summary"], indent=4)
        d_col6.download_button("📄 Summary JSON", summary_json, "summary.json", "application/json", use_container_width=True)

        st.subheader("CSV Preview")
        st.dataframe(df.head(100), use_container_width=True)
"""

with open("dashboard.py", "w") as f:
    f.write(code)

print("dashboard.py updated safely with elegant UI layout")
