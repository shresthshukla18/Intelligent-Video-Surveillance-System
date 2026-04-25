# Intelligent-Video-Surveillance-System-PoC-1

---

#**Project Objective**

The objective of this project is to build an intelligent video surveillance system that goes beyond basic object detection by providing real-time tracking and behavioral analytics from video data. The system aims to extract meaningful insights such as movement patterns, object flow, and crowd behavior from CCTV-like footage.

---

#**Problem Definition**

Traditional surveillance systems only record video, requiring manual monitoring, which is inefficient, time-consuming, and prone to human error.

    This project addresses that problem by:


    1. Automatically detecting objects in video frames
    2. Tracking each object uniquely across frames
    3. Generating analytics such as movement direction, entry/exit counts, and crowd density

The goal is to convert raw video into actionable insights without manual intervention.

---

#**Key Features**

1. Object Detection - Detects multiple object classes such as people, cars, buses, trucks, and motorcycles in each video frame.

2. Multi-Object Tracking - Assigns a unique Track ID to each detected object and maintains it across frames using ByteTrack.

3. Entry and Exit Counting - Counts objects crossing predefined horizontal and vertical lines to determine entry and exit movements.

4. Directional Flow Analysis - Analyzes movement direction (left-to-right, right-to-left, top-to-bottom, bottom-to-top) based on object displacement.

5. Speed Classification - 

       -> Classifies object movement into:
     
       1. Slow
       2. Moderate
       3. Fast
      
6. Crowd Density Heatmap - Generates heatmaps showing high-activity areas based on object movement over time.

7. Annotated Video Output - Produces video with bounding boxes, track IDs, and labels for each detected object.

8. Performance Metrics Logging

       ->Logs frame-wise data such as:

       1. FPS
       2. Inference time
       3. Occupancy
       4. Track creation and loss
   
9. CSV Output Generation - Stores all analytics data in a CSV file for further analysis.

10. Streamlit-Based UI - Provides an interactive dashboard where users can:

        1.Upload or select video

        2.Run pipeline

        3.View outputs (videos, heatmaps, CSV, summary)

---

#**Project Structure**

The project is developed in Google Colab and organized based on logical components derived from notebook cells.

    cv_project/
    │
    ├── videos/                 # Sample input videos
    ├── uploads/               # User uploaded videos (via UI)
    ├── output/                # Generated outputs (auto-created)
    │
    ├── cell_1_setup/          # Environment setup and path configuration
    │   └── setup.py
    │
    ├── cell_2_pipeline/       # Core processing pipeline
    │   └── pipeline.py
    │
    ├── cell_3_helpers/        # Helper functions / utilities (if used)
    │   └── utils.py
    │
    ├── cell_4_ui/             # Streamlit dashboard
    │   └── dashboard.py
    │
    ├── cell_5_runner/         # Execution / integration (if applicable)
    │   └── run.py
    │
    ├── requirements.txt       # Dependencies

Notes : The project is designed to run in Google Colab environment and outputs are automatically saved inside the output/ folder. Each execution creates structured outputs including videos, CSV, and images.

---

#**Installation**

This project is designed to run in a Google Colab environment.

Install the required dependencies using:

    pip install -r requirements.txt

Or install manually:

    pip install opencv-python numpy torch ultralytics supervision streamlit pandas matplotlib

---
    
#**How to Run :**
                     
  1.Open the project in Google Colab.
  
  2.Ensure all required folders (videos/, output/) are accessible in your Drive.
  
  3.Run the cells in order:
   
    1.Setup (paths and environment)
    2.Pipeline
    3.UI (Streamlit)
    
   4.Launch the Streamlit UI.
   
   5.In the UI:
    
    1.Select a sample video OR upload your own
    2.Click Run Pipeline
    3.View results directly in the dashboard

---

#**Outputs Generated**

After running the pipeline, the system automatically generates the following outputs:

1. Annotated Video - Video with bounding boxes, class labels, and Track IDs for each detected object.

2. Heatmap Video - Visual representation of movement intensity across frames, highlighting high-activity areas.

3. Overlay Video - Combination of annotated video and heatmap for combined visualization.

4. Heatmap Image - Final accumulated heatmap showing overall crowd density.

5. CSV File (Performance Log) - Frame-by-frame data including:

       1.Frame number
       2.Inference time
       3.FPS
       4.Occupancy
       5.Entry/Exit counts
       6.Speed classification
       7.Tracks created and lost

6. Summary Output - Final aggregated metrics including:

       1.Total tracks created
       2.Total tracks lost
       3.Peak occupancy
       4.Directional flow
       5.Average FPS

Output Storage - All outputs are automatically saved in:

    /cv_project/output/run_<timestamp>/

Each run creates a separate folder containing all generated files.

---

#**Key Metrics**

1. Tracks Created - Number of objects that were successfully detected and confirmed over multiple frames. A new track is created only after consistent detection to avoid noise.

2. Tracks Lost - Number of tracked objects that disappeared due to occlusion, leaving the frame, or detection failure.

3. Occupancy - Number of active tracked objects present in a frame at a given time.

4. Peak Occupancy - Maximum number of objects present in any single frame during the entire video.

5. Directional Flow - Represents movement trends of objects:

       1.Left to Right
       2.Right to Left
       3.Top to Bottom
       4.Bottom to Top

These values are calculated based on frame-to-frame movement of each tracked object and represent cumulative motion patterns, not individual object counts.

6. Speed Classification - Objects are classified based on movement between frames:

       1.Slow
       2.Moderate
       3.Fast

7. FPS (Frames Per Second) - Indicates how many frames are processed per second, representing system performance.

8. Inference Time - Time taken by the model to process each frame.

---

#**Limitations**

* Tracking may become unstable in cases of heavy occlusion
* Low-light or poor lighting conditions reduce detection accuracy
* Fast-moving objects may temporarily lose tracking
* System relies on pre-trained models and is not fine-tuned for specific environments
* ROI-based analytics and dwell time are not implemented

---

#**Failure Cases**

* **Occlusion:** Overlapping objects may cause ID loss or reassignment
* **Motion Blur:** Fast movement reduces detection confidence
* **Crowded Scenes:** High density may lead to tracking confusion
* **Lighting Variations:** Poor lighting can result in missed detections
* **Perspective Issues:** Distant or small objects may not be detected reliably

---

#**Scalability**

* Current system supports single video input
* Can be extended to multiple camera streams using parallel processing
* Performance can be improved using GPU acceleration
* Lighter models can be used for deployment on edge devices

---

#**Future Improvements**

* Dwell time calculation
* ROI-based analytics
* Model fine-tuning on custom datasets
* Improved tracking stability
* Edge-device optimization

---

#**Conclusion**

This project demonstrates an end-to-end intelligent surveillance system capable of converting raw video data into meaningful insights. By integrating detection, tracking, and analytics, the system provides a foundation for automated monitoring and can be extended further for real-world deployment.

---
