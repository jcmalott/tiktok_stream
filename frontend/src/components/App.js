// const socket = io("ws://localhost:5000");
// For TikFinity - Need upgrade version to work
// const socket = io("ws://localhost:21213/");
import React, { useEffect, useRef, useState } from "react";
import io from "socket.io-client";

const SOCKET_URL = "http://localhost:5000";
const VIDEO_PATH = "/video/";
const SUB_SOUND_PATH = "/sound/sub.mp4";

// Array of follow alert videos
const FOLLOW_ALERTS = [
  "games_ass.mp4",
  "get_me_out.mp4",
  "hate_at_zero.mp4",
  "hot_dogshit.mp4",
  "no_fun.mp4",
  "rat_wars.mp4",
];

function App() {
  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  // Initialize socket connection
  useEffect(() => {
    const newSocket = io(SOCKET_URL, {
      withCredentials: true,
      extraHeaders: {
        "Access-Control-Allow-Origin": "http://localhost.com:3000",
      },
      reconnectionAttempts: 3,
      reconnectionDelay: 1000,
    });

    setSocket(newSocket);

    // Clean up socket connection on component unmount
    return () => {
      if (newSocket) newSocket.disconnect();
    };
  }, []);

  // Set up socket event listeners
  useEffect(() => {
    if (!socket) return;

    // Pre-load subscription sound
    const audioSub = new Audio(SUB_SOUND_PATH);

    // Socket event handlers
    const handleConnect = () => {
      console.log("Connected to server!");
      setIsConnected(true);
      socket.emit("message", "Hello, from Client!");
    };

    const handleDisconnect = () => {
      console.log("Disconnected from server");
      setIsConnected(false);
    };

    const handleMessage = (data) => {
      console.log(`Server: ${data}`);
    };

    const handleFollow = () => {
      console.log("New follower detected!");
      const randomIndex = Math.floor(Math.random() * FOLLOW_ALERTS.length);
      playVideo(FOLLOW_ALERTS[randomIndex]);
    };

    const handleComment = () => {
      playVideo("blerp/headshot.mp4");
    };

    const handleSubscribe = () => {
      audioSub.play().catch((error) => {
        console.error("Failed to play subscription sound:", error);
      });
    };

    const handleError = (error) => {
      console.error("Socket error:", error);
    };

    // Register event listeners
    socket.on("connect", handleConnect);
    socket.on("disconnect", handleDisconnect);
    socket.on("connectEvent", handleConnect);
    socket.on("messageEvent", handleMessage);
    socket.on("followEvent", handleFollow);
    socket.on("commentEvent", handleComment);
    socket.on("subscribeEvent", handleSubscribe);
    socket.on("error", handleError);

    // Clean up event listeners when component unmounts or socket changes
    return () => {
      socket.off("connect", handleConnect);
      socket.off("disconnect", handleDisconnect);
      socket.off("connectEvent", handleConnect);
      socket.off("messageEvent", handleMessage);
      socket.off("followEvent", handleFollow);
      socket.off("commentEvent", handleComment);
      socket.off("subscribeEvent", handleSubscribe);
      socket.off("error", handleError);
    };
  }, [socket]);

  // Play a video with error handling
  const playVideo = (videoFileName) => {
    if (!videoRef.current || !containerRef.current) return;

    try {
      videoRef.current.src = VIDEO_PATH + videoFileName;
      containerRef.current.style.display = "block";

      videoRef.current.play().catch((error) => {
        containerRef.current.style.display = "none";
        socket.emit("message", `ERROR: ${error.message}`);
      });
    } catch (error) {
      console.error("Video setup error:", error);
    }
  };

  // Handle video end event
  const handleVideoEnd = () => {
    if (containerRef.current) {
      containerRef.current.style.display = "none";
    }
  };

  return (
    <>
      {/* Video container */}
      <div
        ref={containerRef}
        className="video-container"
        style={{
          display: "block",
          position: "relative",
          width: "800px",
          height: "540px",
        }}
      >
        <video
          ref={videoRef}
          src={`${VIDEO_PATH}all_stupid_shit.mp4`}
          onEnded={handleVideoEnd}
          width="800"
          height="540"
        ></video>

        <img
          className="discord-logo"
          src="/image/Discord.png"
          alt="Discord Logo"
          style={{
            position: "absolute",
            bottom: "30px",
            right: "21px",
            width: "120px",
          }}
        />
      </div>
    </>
  );
}

export default App;
