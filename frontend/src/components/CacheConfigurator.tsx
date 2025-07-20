import React, { useRef, useState } from 'react';
import axios from 'axios';
import { useMutation } from '@tanstack/react-query';

interface Props {
  onConfigured: () => void;
}

const CacheConfigurator: React.FC<Props> = ({ onConfigured }) => {
  const [path, setPath] = useState('');
  const [success, setSuccess] = useState('');
  const [errorDetail, setErrorDetail] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mutation = useMutation({
    mutationFn: async () => {
      const { data } = await axios.post('/config/cache_path', null, { params: { path } });
      return data as { added: number };
    },
    onSuccess: data => {
      setSuccess(`Success: added ${data.added} records`);
      setTimeout(() => onConfigured(), 1000);
    },
    onError: err => {
      // eslint-disable-next-line no-console
      console.error('Cache configuration failed', err);
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        if (typeof detail === 'string') {
          setErrorDetail(detail);
        }
      }
    },
  });

  function handleBrowse() {
    fileInputRef.current?.click();
  }

  function handleDirSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (files && files.length) {
      const f = files[0] as File & { path?: string; webkitRelativePath?: string };
      if (f.path) {
        const rel = f.webkitRelativePath || '';
        setPath(f.path.slice(0, f.path.length - rel.length));
      }
    }
  }

  return (
    <div className="space-y-2">
      <div>
        <input
          type="text"
          value={path}
          onChange={e => setPath(e.target.value)}
          placeholder="Cache directory path"
        />
        <input
          ref={fileInputRef}
          type="file"
          style={{ display: 'none' }}
          directory=""
          webkitdirectory=""
          onChange={handleDirSelected}
        />
        <button type="button" onClick={handleBrowse} className="ml-1">
          Browse…
        </button>
        <button onClick={() => mutation.mutate()} disabled={!path || mutation.isLoading} className="ml-1">
          Go
        </button>
      </div>
      {success && <div className="text-green-700">{success}</div>}
      {mutation.isError && (
        <div className="text-red-600">
          Failed: {(mutation.error as Error).message}
          {errorDetail && <div>{errorDetail}</div>}
        </div>
      )}
    </div>
  );
};

export default CacheConfigurator;
