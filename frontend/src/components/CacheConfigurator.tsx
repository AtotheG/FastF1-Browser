import React, { useState } from 'react';
import axios from 'axios';
import { useMutation } from '@tanstack/react-query';

interface Props {
  onConfigured: () => void;
}

const CacheConfigurator: React.FC<Props> = ({ onConfigured }) => {
  const [path, setPath] = useState('');
  const mutation = useMutation({
    mutationFn: async () => {
      await axios.post('/config/cache_path', null, { params: { path } });
    },
    onSuccess: () => {
      onConfigured();
    },
  });

  return (
    <div className="space-y-2">
      <div>
        <input
          type="text"
          value={path}
          onChange={e => setPath(e.target.value)}
          placeholder="Cache directory path"
        />
        <button onClick={() => mutation.mutate()} disabled={!path || mutation.isLoading}>
          Go
        </button>
      </div>
      {mutation.isError && (
        <div className="text-red-600">Failed: {(mutation.error as Error).message}</div>
      )}
    </div>
  );
};

export default CacheConfigurator;
