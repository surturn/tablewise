import axios from "axios";

const apiClient = axios.create({
  baseURL: "https://httpbin.org",
  headers: {
    "Content-Type": "application/json",
  },
});

async function run() {
  const formData = new URLSearchParams();
  formData.append("username", "test");
  formData.append("password", "pass");

  const res = await apiClient.post("/post", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  console.log(JSON.stringify(res.data.form));
}

run();
