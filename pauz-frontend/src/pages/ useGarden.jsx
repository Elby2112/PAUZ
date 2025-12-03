import { useState, useEffect } from 'react';
import { gardenAPI, freeJournalAPI } from './gardenAPI';

export const useGarden = () => {
  const [flowers, setFlowers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch garden entries
  const refreshGarden = async () => {
    try {
      setLoading(true);
      setError(null);
      const entries = await gardenAPI.getGardenEntries();
      setFlowers(entries);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Reflect with AI and plant a flower
  const reflectWithAI = async (sessionId) => {
    try {
      const reflection = await freeJournalAPI.reflectWithAI(sessionId);
      
      // Refresh garden to show the new flower
      await refreshGarden();
      
      return reflection;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  // Load garden on mount
  useEffect(() => {
    refreshGarden();
  }, []);

  return {
    flowers,
    loading,
    error,
    refreshGarden,
    reflectWithAI
  };
};