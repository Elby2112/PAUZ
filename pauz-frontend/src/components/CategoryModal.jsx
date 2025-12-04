import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/categoryModal.css";

const CategoryModal = ({ isOpen, onClose, onSelect }) => {
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();

  if (!isOpen) return null;

  const categories = [
    { id: "mind", title: "Mind" },
    { id: "body", title: "Body" },
    { id: "heart", title: "Heart" },
    { id: "family", title: "Family" },
    { id: "friends", title: "Friends" },
    { id: "romance", title: "Romance" },
    { id: "growth", title: "Growth" },
    { id: "money", title: "Money" },
    { id: "mission", title: "Mission" },
    { id: "joy", title: "Joy" },
  ];

  const handleSelect = (cat) => {
    setSelected(cat);
    onSelect(cat);
  };

  const handleProceed = () => {
    navigate("/guidedjournal");
  };

  return (
    <div className="catmodal-overlay" onClick={onClose}>
      <div className="catmodal-box" onClick={(e) => e.stopPropagation()}>
        
        {/* Close Icon */}
        <button className="catmodal-close-icon" onClick={onClose}>✕</button>

        <h3 className="catmodal-title">Choose a Category</h3>

        <div className="catmodal-grid">
          {categories.map((cat) => (
            <button
              key={cat.id}
              className={`catmodal-btn ${selected === cat.id ? "selected" : ""}`}
              onClick={() => handleSelect(cat.id)}
            >
              {cat.title}
            </button>
          ))}
        </div>

        {selected && (
          <button className="catmodal-proceed" onClick={handleProceed}>
            Proceed
          </button>
        )}
      </div>
    </div>
  );
};

export default CategoryModal;
