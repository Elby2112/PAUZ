# 🎯 HINT FEATURE TROUBLESHOOTING GUIDE

## 🚀 **HOW TO DEBUG YOUR HINT FEATURE**

### **Step 1: Check Backend Status**
```bash
# Make sure your backend is running
uvicorn app.main:app --reload

# Test the hint endpoint directly
curl -X POST "http://localhost:8000/freejournal/test-session/hints" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"current_content": "I am feeling grateful today"}'
```

### **Step 2: Check Browser Console**
Open your browser's developer tools (F12) and check:
1. **Console tab** for JavaScript errors
2. **Network tab** for API requests
3. **Application tab** for localStorage

### **Step 3: Check Authentication**
```javascript
// In browser console
console.log("Token:", localStorage.getItem("pauz_token"));
console.log("Headers:", {
  "Content-Type": "application/json",
  "Authorization": `Bearer ${localStorage.getItem("pauz_token")}`
});
```

## 🔍 **COMMON ISSUES & SOLUTIONS**

### **Issue 1: CORS Error**
**Symptoms:**
- "CORS error: Cannot connect to backend"
- Network tab shows failed request

**Solution:**
```bash
# Check your backend CORS configuration
# In app/main.py, make sure you have:
origins = [
    "http://localhost:5173",  # Your frontend port
    "http://localhost:3000",
]

# Restart backend after changes
```

### **Issue 2: Authentication Error**
**Symptoms:**
- 401 Unauthorized errors
- "Please log in again"

**Solution:**
```javascript
// Check if token exists and is valid
const token = localStorage.getItem("pauz_token");
if (!token) {
    console.log("No token found - redirect to login");
    window.location.href = "/login";
}
```

### **Issue 3: Session Not Created**
**Symptoms:**
- "Could not create session for hint"
- Session ID is null

**Solution:**
```javascript
// Add debug logging to createSession function
console.log("Creating session...");
const res = await fetch(`${API_BASE}/freejournal/`, {
    method: "POST",
    headers: getAuthHeaders(),
});
console.log("Response status:", res.status);
console.log("Response:", await res.json());
```

### **Issue 4: Hint Request Fails**
**Symptoms:**
- Loading spinner never stops
- Error message appears

**Solution:**
```javascript
// Add detailed logging to requestHint
try {
    console.log("Requesting hint for session:", sid);
    console.log("Current text:", text);
    
    const res = await fetch(`${API_BASE}/freejournal/${sid}/hints`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ current_content: text || "" }),
    });
    
    console.log("Response status:", res.status);
    const hintData = await res.json();
    console.log("Hint received:", hintData);
    
} catch (error) {
    console.error("Full error:", error);
    console.error("Error stack:", error.stack);
}
```

## 🧪 **TESTING CHECKLIST**

### **✅ Pre-Flight Checks**
- [ ] Backend is running on `http://localhost:8000`
- [ ] Can access `http://localhost:8000/docs`
- [ ] Frontend is running (usually on `http://localhost:5173`)
- [ ] User is logged in (token in localStorage)

### **✅ API Testing**
- [ ] Test session creation: `POST /freejournal/`
- [ ] Test hint generation: `POST /freejournal/{session_id}/hints`
- [ ] Test hint retrieval: `GET /freejournal/{session_id}/hints`

### **✅ Frontend Testing**
- [ ] Hint button is clickable
- [ ] Loading state appears
- [ ] Hint appears in panel
- [ ] "Use" button works
- [ ] Hint is added to textarea

## 🔧 **ENHANCED DEBUGGING COMPONENT**

Add this to your FreeJournal component:

```javascript
// Debug component - add before return statement
const DebugPanel = () => {
  const [showDebug, setShowDebug] = React.useState(false);
  
  return (
    <>
      <button 
        onClick={() => setShowDebug(!showDebug)}
        style={{ position: 'fixed', top: 10, right: 10, zIndex: 9999 }}
      >
        🐛 Debug
      </button>
      
      {showDebug && (
        <div style={{
          position: 'fixed', top: 50, right: 10, 
          background: 'white', border: '1px solid black',
          padding: 10, zIndex: 9999, fontSize: '12px'
        }}>
          <h4>Debug Info</h4>
          <p>Session ID: {sessionId || 'null'}</p>
          <p>Token: {localStorage.getItem('pauz_token') ? '✅' : '❌'}</p>
          <p>Text length: {text.length}</p>
          <p>Hints count: {hints.length}</p>
          <p>Loading: {hintLoading ? '🔄' : '✅'}</p>
          <p>Error: {error || 'none'}</p>
          
          <button onClick={() => {
            console.log("Full state:", {
              sessionId, text, hints, hintLoading, error
            });
          }}>
            Log State
          </button>
          
          <button onClick={() => {
            createSession();
          }}>
            Create Session
          </button>
        </div>
      )}
    </>
  );
};

// Add to JSX before closing div:
return (
  <div className="freejournal-container">
    <DebugPanel />
    {/* ... rest of your component */}
  </div>
);
```

## 📞 **GETTING HELP**

If you're still stuck:

1. **Check the browser console** - most errors appear there
2. **Check the Network tab** - see if requests are being sent
3. **Test the backend directly** - use curl or Postman
4. **Share the exact error message** - not just "it doesn't work"
5. **Share your browser console errors** - very helpful for debugging

## 🎯 **QUICK TEST**

Test this simple flow:

1. **Open browser console** (F12)
2. **Navigate to your journal page**
3. **Click hint button**
4. **Check console logs** - you should see:
   ```
   🎯 Requesting hint...
   📝 Creating new session for hint...
   ✅ Session created: abc-123
   🚀 Sending hint request to backend...
   📊 Response status: 200
   ✅ Hint received: {hint_text: "What are you grateful for..."}
   ```

If you see all these logs, your hint feature is working! 🎉