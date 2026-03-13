import React from 'react';

const AdminPanel: React.FC = () => {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
        Admin Panel
      </h1>

      <div className="card">
        <p className="text-gray-600 dark:text-gray-400">
          Administrative interface for challenge management and platform oversight.
        </p>
      </div>
    </div>
  );
};

export default AdminPanel;