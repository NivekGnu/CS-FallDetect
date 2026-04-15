const videoUrl = "http://localhost:8000/video_feed";

function LiveVideo() {
  return (
    <img src={videoUrl} alt="Live Video Feed" style={{ width: "100%" }} />
  );
}

export default LiveVideo;