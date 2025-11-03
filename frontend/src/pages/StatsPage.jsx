import React, { useEffect, useState } from "react";
import api from "../api";
import DatabaseSelector from "../components/DatabaseSelector";
import DatabaseStats from "../components/DatabaseStats";

const StatsPage = () => {
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState(null);
  const [tableCount, setTableCount] = useState(null);
  const [columnCount, setColumnCount] = useState(null);
  const [pkCount, setPkCount] = useState(null);
  const [fkCount, setFkCount] = useState(null);
  const [ukCount, setUkCount] = useState(null);
  const [recordCount, setRecordCount] = useState(null);
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
      setTableCount(res.data.count);
    } catch (err) {
      console.error("Error fetching table count:", err);
      setTableCount(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchColumnCount = async (dbId) => {
    if (!dbId) return;
    setLoading(true);
    try {
      const res = await api.get(`/databases/${dbId}/columns/count`);
      setColumnCount(res.data.count);
    } catch (err) {
      console.error("Error fetching column count:", err);
      setColumnCount(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchPkCount = async (dbId) => {
    if (!dbId) return;
    setLoading(true);
    try {
      const res = await api.get(`/databases/${dbId}/keys/primary/count`);
      setPkCount(res.data.count);
    } catch (err) {
      console.error("Error fetching primary key count:", err);
      setPkCount(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchFkCount = async (dbId) => {
    if (!dbId) return;
    setLoading(true);
    try {
      const res = await api.get(`/databases/${dbId}/keys/foreign/count`);
      setFkCount(res.data.count);
    } catch (err) {
      console.error("Error fetching foreign key count:", err);
      setFkCount(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchUkCount = async (dbId) => {
    if (!dbId) return;
    setLoading(true);
    try {
      const res = await api.get(`/databases/${dbId}/keys/unique/count`);
      setUkCount(res.data.count);
    } catch (err) {
      console.error("Error fetching unique key count:", err);
      setUkCount(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecordCount = async (dbId) => {
    if (!dbId) return;
    setLoading(true);
    try {
      const res = await api.get(`/databases/${dbId}/records/count`);
      setRecordCount(res.data.count);
    } catch (err) {
      console.error("Error fetching record count:", err);
      setRecordCount(null);
    } finally {
      setLoading(false);
    }
  };


  const handleSelectChange = (dbId) => {
    setSelectedDb(dbId);
    fetchTableCount(dbId);
    fetchColumnCount(dbId);
    fetchPkCount(dbId);
    fetchFkCount(dbId);
    fetchUkCount(dbId);
    fetchRecordCount(dbId);
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
                columnCount={columnCount}
                pkCount={pkCount}
                fkCount={fkCount}
                ukCount={ukCount}
                recordCount={recordCount}
                selectedDb={selectedDb}
            />
        </div>
    </div>
  );
};

export default StatsPage;
