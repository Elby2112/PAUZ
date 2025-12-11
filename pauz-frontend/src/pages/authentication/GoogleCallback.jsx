import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

function GoogleCallback() {
  const navigate = useNavigate();
  const hasRun = useRef(false); // Prevent double execution

  const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

  useEffect(() => {
    if (hasRun.current) return; // Prevent StrictMode double calls
    hasRun.current = true;

    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);

      const token = urlParams.get("token");
      const email = urlParams.get("email");
      const name = urlParams.get("name");
      const error = urlParams.get("error");
      const code = urlParams.get("code");
      const state = urlParams.get("state");

      console.log("🔍 URL Params:", {
        token,
        email,
        name,
        error,
        code,
        state,
      });

      // ----------------------------------------
      // ❌ HANDLE BACKEND ERRORS
      // ----------------------------------------
      if (error) {
        alert("Login failed: " + error);
        navigate("/");
        return;
      }

      // ----------------------------------------
      // ✅ CASE 1 — BACKEND ALREADY EXCHANGED GOOGLE CODE
      // ----------------------------------------
      if (token) {
        console.log("🎉 Using backend token (redirect mode)");
        await completeLogin(token);
        return;
      }

      // ----------------------------------------
      // ✅ CASE 2 — FRONTEND MUST EXCHANGE CODE WITH BACKEND
      // ----------------------------------------
      if (code && state) {
        console.log("🔄 Using frontend token exchange flow...");

        try {
          const response = await fetch("http://155.138.238.152:8000/auth/token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code, state }),
          });

          if (!response.ok) {
            const errData = await response.json();
            console.error("❌ /auth/token failed:", errData);

            alert(errData.detail || "Login failed during token exchange.");
            navigate("/");
            return;
          }

          const data = await response.json();
          console.log("✅ Token exchange successful");

          await completeLogin(data.access_token);
          return;
        } catch (err) {
          console.error("❌ Google login error:", err);
          alert("Login failed: " + err.message);
          navigate("/");
          return;
        }
      }

      // ----------------------------------------
      // ❌ CASE 3 — NOTHING PROVIDED
      // ----------------------------------------
      console.error("❌ No token, no code. Cannot authenticate.");
      alert("Login failed. Please try again.");
      navigate("/");
    };

    // -------------------------------------------------
    // 🔥 LOGIN COMPLETER — USED BY BOTH FLOWS
    // -------------------------------------------------
    const completeLogin = async (accessToken) => {
      try {
        // Save token
        localStorage.setItem("pauz_token", accessToken);

        // Fetch full user info (email, name, picture)
        //http://155.138.238.152:8000
        const userResponse = await fetch("http://155.138.238.152:8000/auth/me", {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        if (userResponse.ok) {
          const userData = await userResponse.json();

          console.log("🖼️ User data:", userData);

          localStorage.setItem(
            "pauz_user",
            JSON.stringify({
              email: userData.email,
              name: userData.name,
              picture: userData.picture,
            })
          );
        } else {
          console.warn("⚠️ Could not fetch complete user info");
        }

        // Redirect to the app
        if (isSafari) {
          window.location.href = "/guided-journal";
        } else {
          navigate("/guided-journal");
        }
      } catch (error) {
        console.error("❌ Error completing login:", error);
        alert("Unexpected login error. Please try again.");
        navigate("/");
      }
    };

    handleCallback();
  }, [navigate, isSafari]);

  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-lg">Completing authentication...</p>
        <p className="text-sm text-gray-600 mt-2">This should only take a moment</p>
      </div>
    </div>
  );
}

export default GoogleCallback;
