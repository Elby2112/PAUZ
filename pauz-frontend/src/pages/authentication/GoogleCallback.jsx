import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function GoogleCallback() {
const navigate = useNavigate();
const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

useEffect(() => {
const handleGoogleCallback = async () => {
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get("code");
const state = urlParams.get("state");


  if (!code || !state) {
    console.error("Missing code or state in callback URL");
    navigate("/");
    return;
  }

  try {
    // Call backend /auth/token
    const tokenRes = await fetch("http://localhost:8000/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, state }),
    });

    if (!tokenRes.ok) {
      const errText = await tokenRes.text();
      throw new Error(`Request failed: ${tokenRes.status} - ${errText}`);
    }

    const tokenData = await tokenRes.json();
    localStorage.setItem("pauz_token", tokenData.access_token);

    // Fetch user data
    const meRes = await fetch("http://localhost:8000/auth/me", {
      headers: { Authorization: `Bearer ${tokenData.access_token}` },
    });

    if (!meRes.ok) {
      throw new Error(`Failed to fetch user: ${meRes.status}`);
    }

    const userData = await meRes.json();
    localStorage.setItem("pauz_user", JSON.stringify(userData));

    // Navigate to homepage or guided journaling
    if (isSafari) {
      window.location.href = "/"; // Safari needs hard reload
    } else {
      navigate("/guided-journal"); // Redirect to journal page
    }

  } catch (err) {
    console.error("Google login error:", err);
    navigate("/");
  }
};

handleGoogleCallback();


}, [navigate, isSafari]);

return ( <div className="flex justify-center items-center min-h-screen"> <p className="text-lg">Connecting to Google...</p> </div>
);
}

export default GoogleCallback;
