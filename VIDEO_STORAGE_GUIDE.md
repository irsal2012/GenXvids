# 📁 GenXvids Video Storage Guide

## 🎯 Where Are Generated Videos Stored?

Your generated videos are stored in the **`apps/backend/uploads/videos/`** directory on the server.

## 📂 Storage Structure

```
GenXvids/
├── apps/
│   └── backend/
│       └── uploads/
│           ├── videos/           ← 🎬 Your videos are here!
│           ├── thumbnails/       ← 🖼️ Video thumbnails
│           ├── assets/           ← 📁 Other assets
│           └── temp/             ← 🗂️ Temporary files
```

## 📋 Current Video Files

Based on the current directory listing:

```bash
apps/backend/uploads/videos/
├── video_1_e6905918.mp4     (1,371 bytes)
├── video_2_20f5f2f8.html    (79,955 bytes)
└── video_3_35faf073.html    (44,995 bytes)
```

## 🔗 How to Access Your Videos

### **1. Through the Web Interface**
When you generate a video, you'll receive a success message with:
- **Video ID**: Unique identifier for your video
- **Direct Links**: URLs to view/download your video
- **Storage Location**: File path information

### **2. Direct API Access**
- **View HTML Preview**: `/api/v1/videos/{video_id}/view`
- **Download File**: `/api/v1/videos/{video_id}/download`
- **Get Video Info**: `/api/v1/videos/{video_id}`

### **3. File System Access**
Videos are stored with naming pattern: `video_{id}_{random_hash}.{extension}`

## 🎞️ Video Formats

### **HTML Preview (Default)**
- **Format**: Interactive HTML file with embedded frames
- **Size**: ~45-80KB per video
- **Features**: 
  - Play/pause controls
  - Frame navigation
  - Progress bar
  - Professional styling
  - Auto-play functionality

### **MP4 Video (With FFmpeg)**
- **Format**: Standard MP4 video file
- **Size**: Varies based on duration and quality
- **Requirements**: FFmpeg must be installed
- **Installation**: `brew install ffmpeg` (macOS)

## 📊 Video Metadata

Each video includes comprehensive metadata:

```json
{
  "duration": 10,
  "resolution": "1280x720",
  "fileSize": 79955,
  "format": "html",
  "fps": 30,
  "quality": "medium",
  "aspectRatio": "16:9",
  "frameCount": 300
}
```

## 🔐 Security & Access Control

### **Authenticated Endpoints**
- `/api/v1/videos/{video_id}/download` - Requires user authentication
- `/api/v1/videos/{video_id}` - Requires user authentication
- Users can only access their own videos

### **Public Endpoints**
- `/api/v1/videos/{video_id}/view` - No authentication required (HTML previews only)

## 💾 Database Storage

Video information is also stored in the database with:

```sql
videos table:
├── id (Primary Key)
├── title
├── description
├── status (queued/processing/completed/failed)
├── file_path (Full path to video file)
├── thumbnail_path
├── duration
├── file_size
├── resolution
├── format
├── video_metadata (JSON with detailed info)
├── user_id (Owner)
├── created_at
└── updated_at
```

## 🎬 Example Success Message

When you generate a video, you'll see:

```
🎉 Video generated successfully!

📹 Video ID: 3
📊 Status: completed
⏱️ Duration: 10 seconds
🎞️ Format: html
📐 Resolution: 1280x720

📁 Your video is stored in: apps/backend/uploads/videos/

🔗 Access your video:
• View: /api/v1/videos/3/view
• Download: /api/v1/videos/3/download

💡 Your video has been generated as an interactive HTML preview. 
Install FFmpeg for MP4 generation.
```

## 🚀 Quick Access Methods

### **Method 1: Click the Link**
After generation, click "Yes" when prompted to view your video immediately.

### **Method 2: Direct URL**
Navigate to: `http://localhost:8000/api/v1/videos/{your_video_id}/view`

### **Method 3: File System**
Browse to: `apps/backend/uploads/videos/` and open the HTML file directly.

## 🔧 Troubleshooting

### **Video Not Found**
- Check if the video ID is correct
- Verify you're logged in (for download endpoint)
- Ensure the video generation completed successfully

### **File Access Issues**
- Check file permissions in uploads directory
- Verify the backend server is running
- Confirm the file exists in the uploads/videos/ directory

### **Want MP4 Instead of HTML?**
1. Install FFmpeg: `brew install ffmpeg`
2. Restart the backend server
3. Generate a new video
4. The system will automatically create MP4 files

## 📱 Mobile & Sharing

### **HTML Previews**
- Work on all devices with web browsers
- Can be shared via direct links
- Self-contained with embedded frames
- No additional software required

### **MP4 Videos**
- Compatible with all video players
- Can be uploaded to social media
- Smaller file sizes for longer videos
- Better for professional use

---

**Your videos are safely stored and easily accessible through multiple methods!** 🎬✨
