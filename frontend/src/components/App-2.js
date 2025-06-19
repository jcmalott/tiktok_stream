import React, { useEffect, useRef } from "react";
import io from "socket.io-client";

// const socket = io("ws://localhost:5000");
// For TikFinity - Need upgrade version to work
// const socket = io("ws://localhost:21213/");

function App() {
  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const vidPath = "/video/";
  const audioSub = new Audio("/sound/sub.mp4");
  const socket = io("http://localhost:5000");

  const followAlert = [
    "games_ass.mp4",
    "get_me_out.mp4",
    "hate_at_zero.mp4",
    "hot_dogshit.mp4",
    "no_fun.mp4",
    "rat_wars",
  ];

  useEffect(() => {
    socket.on("connectEvent", () => {
      console.log("Connected to Server!");
      socket.emit("message", "Hello, from Client!");
    });
    socket.on("messageEvent", (data) => {
      console.log(`Server: ${data}`);
    });
    socket.on("followEvent", (data) => {
      console.log("Following");
      handlePlayPause(
        followAlert[Math.floor(Math.random() * (followAlert.length - 1))]
      );
    });
    socket.on("commentEvent", (data) => {
      handlePlayPause("blerp/headshot.mp4");
    });
    // socket.on("giftEvent", (data) => {
    // });
    socket.on("subscribeEvent", (data) => {
      audioSub.play();
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const handlePlayPause = (soundPath) => {
    videoRef.current.src = vidPath + soundPath;
    containerRef.current.style.display = "block";
    videoRef.current.play().catch((e) => {
      containerRef.current.style.display = "none";
      socket.emit("message", `ERROR: ${e}`);
      console.log(`ERROR: ${e}`);
    });
  };

  const handleVideoEnd = () => {
    containerRef.current.style.display = "none";
  };

  // const sendMessage = () => {
  //   socket.emit("message", "Hello, from React!");
  // };

  return (
    <div ref={containerRef} className="container" style={{ display: "none" }}>
      <video
        ref={videoRef}
        src="/video/all_stupid_shit.mp4"
        onEnded={handleVideoEnd}
        width="750"
        height="500"
      ></video>
      <img className="discord-logo" src="/image/Discord.png" alt="" />
    </div>
  );
}

export default App;
