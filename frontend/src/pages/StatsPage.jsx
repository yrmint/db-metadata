import React, { useEffect, useState } from "react";
import api from "../api";
import DatabaseSelector from "../components/DatabaseSelector";
import DatabaseStats from "../components/DatabaseStats";

const StatsPage = () => {
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState(null);
  const [tableCount, setTableCount] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/databases/")
      .then((res) => setDatabases(res.data))
      .catch(console.error);
  }, []);

  const fetchTableCount = async (dbId) => {
    if (!dbId) return;
    setLoading(true);
    try {
      const res = await api.get(`/databases/${dbId}/tables/count`);
      setTableCount(res.data.table_count);
    } catch (err) {
      console.error("Error fetching table count:", err);
      setTableCount(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectChange = (dbId) => {
    setSelectedDb(dbId);
    fetchTableCount(dbId);
  };

  return (
    <div>
        <h2 className="text-2xl font-semibold">Statistics</h2>
            <div className="database-container">
            <DatabaseSelector
                databases={databases}
                selectedDb={selectedDb}
                onSelect={handleSelectChange}
            />
            <DatabaseStats
                loading={loading}
                tableCount={tableCount}
                selectedDb={selectedDb}
            />
        </div>
    </div>
  );
};

export default StatsPage;
