import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function GoogleCallback() {
  const navigate = useNavigate();
  const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

  useEffect(() => {
    const handleGoogleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get("token");
      const email = urlParams.get("email");
      const name = urlParams.get("name");
      const error = urlParams.get("error");
      const code = urlParams.get("code");
      const state = urlParams.get("state");

      console.log("🔍 GoogleCallback - URL params:", {
        token: token ? "present" : "missing",
        email: email || "missing", 
        name: name || "missing",
        error: error || "none",
        code: code ? "present" : "missing",
        state: state || "missing"
      });

      // Handle OAuth errors
      if (error) {
        console.error("❌ OAuth error returned from backend:", error);
        alert("Login failed: " + error);
        navigate("/");
        return;
      }

      // Case 1: We have token from backend redirect (this happens if GET /auth/callback was processed)
      if (token && email) {
        try {
          console.log("✅ Token received from backend redirect");
          
          // Store token and user data
          localStorage.setItem("pauz_token", token);
          localStorage.setItem("pauz_user", JSON.stringify({
            email: email,
            name: name || "User",
            picture: null // Will be updated when we fetch from /auth/me
          }));
          
          console.log("✅ User data saved:", email);

          // Fetch complete user data including picture
          try {
            const userResponse = await fetch("http://localhost:8000/auth/me", {
              headers: {
                "Authorization": `Bearer ${token}`,
              },
            });

            if (userResponse.ok) {
              const userData = await userResponse.json();
              console.log("🖼️ Complete user data received:", userData);
              
              // Update localStorage with complete user data including picture
              localStorage.setItem("pauz_user", JSON.stringify({
                email: userData.email,
                name: userData.name,
                picture: userData.picture // ✅ INCLUDE THE PICTURE!
              }));
              
              console.log("✅ Complete user data saved with picture:", userData.picture ? "YES" : "NO");
            } else {
              console.warn("⚠️ Could not fetch complete user info");
            }
          } catch (userError) {
            console.warn("⚠️ Error fetching complete user info:", userError);
          }

          // Navigate to homepage or guided journaling
          if (isSafari) {
            console.log("🍎 Safari detected, using hard redirect");
            window.location.href = "/guided-journal"; // Safari needs hard reload
          } else {
            console.log("🌐 Navigating to guided journal");
            navigate("/guided-journal"); // Redirect to journal page
          }

          return;
        } catch (err) {
          console.error("❌ Error saving token from redirect:", err);
          alert("An unexpected error occurred during login. Please try again.");
          navigate("/");
          return;
        }
      }

      // Case 2: We have authorization code (Google redirected directly to frontend)
      if (code && state) {
        console.log("🔄 Authorization code received from Google, exchanging for token...");
        
        try {
          // Exchange code for token
          const response = await fetch("http://localhost:8000/auth/token", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ code, state }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            console.error("❌ Token exchange failed:", errorData);
            
            // Check for specific error messages
            if (errorData.message) {
              if (errorData.message.includes("already used")) {
                console.log("💡 Error: Authorization code was already used");
                console.log("💡 This might happen if the backend also processed the callback");
                alert("Authentication conflict detected. The login may have already succeeded. Please check if you're logged in or try again.");
              } else if (errorData.message.includes("expired")) {
                console.log("💡 Error: Authorization code expired");
                alert("Login session expired. Please try logging in again.");
              } else {
                alert("Login failed: " + errorData.message);
              }
            } else {
              throw new Error(`Request failed: ${response.status}`);
            }
            
            navigate("/");
            return;
          }

          const data = await response.json();
          console.log("✅ Token exchange successful");
          
          // Store token
          localStorage.setItem("pauz_token", data.access_token);
          
          // Fetch complete user info including picture
          try {
            const userResponse = await fetch("http://localhost:8000/auth/me", {
              headers: {
                "Authorization": `Bearer ${data.access_token}`,
              },
            });

            if (userResponse.ok) {
              const userData = await userResponse.json();
              console.log("🖼️ Complete user data received:", userData);
              
              // ✅ SAVE COMPLETE USER DATA INCLUDING PICTURE
              localStorage.setItem("pauz_user", JSON.stringify({
                email: userData.email,
                name: userData.name,
                picture: userData.picture // ✅ THIS IS THE FIX!
              }));
              
              console.log("✅ User data saved with picture:", userData.picture ? "YES" : "NO");
            } else {
              console.warn("⚠️ Could not fetch user info, but login was successful");
              // Fallback - save basic data
              localStorage.setItem("pauz_user", JSON.stringify({
                email: email,
                name: name || "User",
                picture: null
              }));
            }
          } catch (userError) {
            console.warn("⚠️ Error fetching user info:", userError);
            // Fallback - save basic data
            localStorage.setItem("pauz_user", JSON.stringify({
              email: email,
              name: name || "User",
              picture: null
            }));
          }

          // Navigate to homepage or guided journaling
          if (isSafari) {
            console.log("🍎 Safari detected, using hard redirect");
            window.location.href = "/guided-journal";
          } else {
            console.log("🌐 Navigating to guided journal");
            navigate("/guided-journal");
          }

        } catch (err) {
          console.error("❌ Google login error:", err);
          alert("Login failed: " + err.message);
          navigate("/");
        }
      } else {
        // Case 3: No authentication data found
        console.error("❌ Missing authentication data in callback URL");
        console.error("❌ URL params:", Object.fromEntries(urlParams.entries()));
        alert("Login failed: Missing authentication data. Please try logging in again.");
        navigate("/");
      }
    };

    handleGoogleCallback();
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