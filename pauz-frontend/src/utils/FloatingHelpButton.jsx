// FloatingHelpButton.jsx — With Draggable Movement
import React, { useState, useEffect, useRef } from "react";
import "../styles/floatingButton.css";
import VoiceAssistant from "./VoiceAssistant";
import "../styles/voiceAssistant.css";

const FloatingHelpButton = () => {
  const [showAssistant, setShowAssistant] = useState(false);
  const [autoPlayWelcome, setAutoPlayWelcome] = useState(false);
  const [isFirstVisit, setIsFirstVisit] = useState(false);

  // Position state
  const [pos, setPos] = useState({ x: 24, y: 24 }); // initial: bottom-right
  const btnRef = useRef(null);
  const dragging = useRef(false);
  const offset = useRef({ x: 0, y: 0 });

  // Detect first visit
  useEffect(() => {
    const hasVisited = localStorage.getItem("pauz_has_visited_before");
    if (!hasVisited) {
      setIsFirstVisit(true);
    }
  }, []);

  // Open assistant manually
  const openAssistant = () => {
    setShowAssistant(true);
    setAutoPlayWelcome(true);
  };

  // Close assistant
  const handleAssistantClose = () => {
    setShowAssistant(false);
    setAutoPlayWelcome(false);

    if (isFirstVisit) {
      localStorage.setItem("pauz_has_visited_before", "true");
      setIsFirstVisit(false);
    }
  };

  // === DRAG FUNCTIONS ==========================
  const startDrag = (e) => {
    dragging.current = true;

    const rect = btnRef.current.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;

    offset.current = {
      x: clientX - rect.left,
      y: clientY - rect.top,
    };
  };

  const onDrag = (e) => {
    if (!dragging.current) return;

    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;

    setPos({
      x: window.innerWidth - (clientX - offset.current.x) - rectWidth(),
      y: window.innerHeight - (clientY - offset.current.y) - rectHeight(),
    });
  };

  const endDrag = () => {
    dragging.current = false;
  };

  const rectWidth = () => btnRef.current?.offsetWidth || 0;
  const rectHeight = () => btnRef.current?.offsetHeight || 0;
  // ==================================================

  return (
    <>
      {/* Floating Help Button — Draggable */}
      <button
        ref={btnRef}
        className={`floating-help-btn ${isFirstVisit ? "first-visit" : ""}`}
        onClick={openAssistant}
        title="Need help?"
        style={{
          position: "fixed",
          right: `${pos.x}px`,
          bottom: `${pos.y}px`,
          touchAction: "none",
        }}
        onMouseDown={startDrag}
        onMouseMove={onDrag}
        onMouseUp={endDrag}
        onMouseLeave={endDrag}
        onTouchStart={startDrag}
        onTouchMove={onDrag}
        onTouchEnd={endDrag}
      >
        Need Help?
      </button>

      {/* Voice Assistant */}
      <VoiceAssistant
        isVisible={showAssistant}
        onClose={handleAssistantClose}
        autoPlayWelcome={autoPlayWelcome}
      />
    </>
  );
};

export default FloatingHelpButton;
