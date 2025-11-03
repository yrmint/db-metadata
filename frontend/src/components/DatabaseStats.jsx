import React from "react";

const DatabaseStats = ({ loading, tableCount, columnCount, pkCount, fkCount, ukCount, recordCount, selectedDb }) => {
  if (!selectedDb) return null;

  return (
    <div className="db-stats">
      {loading && <p>Loading...</p>}

      {!loading && tableCount !== null && (
        <table className="stats-table">
          <tbody>
            <tr>
              <td><strong>Tables count:</strong></td>
              <td>{tableCount}</td>
            </tr>
            <tr>
              <td><strong>Columns count:</strong></td>
              <td>{columnCount}</td>
            </tr>
            <tr>
              <td><strong>Primary keys count:</strong></td>
              <td>{pkCount}</td>
            </tr>
            <tr>
              <td><strong>Foreign keys count:</strong></td>
              <td>{fkCount}</td>
            </tr>
            <tr>
              <td><strong>Unique keys count:</strong></td>
              <td>{ukCount}</td>
            </tr>
            <tr>
              <td><strong>Records count:</strong></td>
              <td>{recordCount}</td>
            </tr>
          </tbody>
        </table>
      )}

      {!loading && tableCount === null && (
        <p style={{ color: "red" }}>Failed to load data.</p>
      )}
    </div>
  );
};

export default DatabaseStats;
