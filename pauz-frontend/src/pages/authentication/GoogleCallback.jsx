import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function GoogleCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");
    const state = urlParams.get("state");

    if (!code) return;

    fetch(`http://localhost:8000/auth/callback?code=${code}&state=${state}`)
      .then(res => res.json())
      .then(data => {
        if (data.access_token) {
          localStorage.setItem("pauz_token", data.access_token);

          // Trigger Navbar update
          window.dispatchEvent(new Event('storage'));

          navigate("/"); // redirect home
        }
      })
      .catch(err => console.error("Google login error:", err));
  }, []);

  return <p>Connecting to Google...</p>;
}

export default GoogleCallback;
