import React, { useEffect, useState } from 'react';
import api from '../api';

const DatabaseList = () => {
    const [databases, setDatabases] = useState([]);
    
    useEffect(() => {
        api.get("/databases")
        .then((res) => setDatabases(res.data))
        .catch(console.error);
    }, []);

    return (
        <div>
            <h2>Databases List</h2>
            <ul>
                {databases.map((db) => (
                    <li key={db.db_id}>{db.db_name}</li>
                ))}
            </ul>
        </div>
    );
};

export default DatabaseList;
