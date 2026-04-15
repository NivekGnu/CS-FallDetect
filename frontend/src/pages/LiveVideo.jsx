import { useState, useEffect } from "react";

const videoUrl = "http://localhost:8000/video_feed";
const statusUrl = "http://localhost:8000/status";

function LiveVideo() {
  const [status, setStatus] = useState({ fall_detected: false });

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await fetch(statusUrl);
      const data = await res.json();
      setStatus(data);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <img src={videoUrl} alt="Live Video Feed" style={{ width: "100%" }} />
      <div style={{
        padding: "10px",
        backgroundColor: status.fall_detected ? "red" : "green",
        color: "white"
      }}>
        {status.fall_detected ? "FALL DETECTED" : "Monitoring"}
      </div>
    </div>
  );
}