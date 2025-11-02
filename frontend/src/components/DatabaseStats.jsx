import React from "react";

const DatabaseStats = ({ loading, tableCount, selectedDb }) => {
  if (!selectedDb) return null;

  return (
    <div className="db-stats">
      {loading && <p>Loading...</p>}
      {!loading && tableCount !== null && (
        <p>
          <strong>Tables count:</strong> {tableCount}
        </p>
      )}
      {!loading && tableCount === null && (
        <p style={{ color: "red" }}>Failed to load data.</p>
      )}
    </div>
  );
};

export default DatabaseStats;
