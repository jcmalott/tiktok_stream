import axios from "axios";

export const connect = async () => {
  const res = await axios.get("/api");
  console.log("RES: ", res);
  return res.data;
};
