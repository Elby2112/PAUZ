import React from "react";
import profileIcon from "../../assets/icons/profile.png";
import freeJournalIcon from "../../assets/images/freejournal.png";
import guidedJournalIcon from "../../assets/images/guidedjournal.png";
import { useNavigate } from "react-router-dom";
import "../../styles/profile.css";

const Profile = () => {
  const navigate = useNavigate();

  const totalJournals = 12;
  const freeJournals = 7;
  const guidedJournals = 5;

  const user = JSON.parse(localStorage.getItem("pauz_user")) ?? {};

  return (
    <div className="profile-container">
      <div className="profile-card">

        {/* Profile Header */}
        <div className="profile-header">
          <img
            src={user.picture || profileIcon}
            alt="Profile Avatar"
            className="profile-avatar"
            crossOrigin="anonymous"
          />
          <h2 className="profile-name">{user.name || "Unknown User"}</h2>
          <p className="profile-email">{user.email || ""}</p>
        </div>

        {/* Journal Summary */}
        <div className="journal-summary">
          <div className="journal-card">
            <img src={freeJournalIcon} alt="Free Journal" />
            <div className="journal-info">
              <span className="journal-count">{freeJournals}</span>
              <span className="journal-label">Free Journals</span>
            </div>
          </div>

          <div className="journal-card">
            <img src={guidedJournalIcon} alt="Guided Journal" />
            <div className="journal-info">
              <span className="journal-count">{guidedJournals}</span>
              <span className="journal-label">Guided Journals</span>
            </div>
          </div>

          <div className="journal-card total">
            <img src={profileIcon} alt="Total Journals" />
            <div className="journal-info">
              <span className="journal-count">{totalJournals}</span>
              <span className="journal-label">Total Journals</span>
            </div>
          </div>
        </div>

        <button
          className="profile-btn garden-btn"
          onClick={() => navigate("/garden")}
        >
          Visit My Garden
        </button>
      </div>
    </div>
  );
};

export default Profile;
