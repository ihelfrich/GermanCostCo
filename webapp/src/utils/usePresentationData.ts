import { useEffect, useMemo, useState } from "react";
import type { PresentationData } from "../types";

interface UsePresentationDataResult {
  loading: boolean;
  error: string | null;
  data: PresentationData | null;
}

export function usePresentationData(): UsePresentationDataResult {
  const [data, setData] = useState<PresentationData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const url = `${import.meta.env.BASE_URL}data/presentation_data.json`;

    fetch(url)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Unable to load data from ${url}`);
        }
        return response.json();
      })
      .then((payload: PresentationData) => {
        setData(payload);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return useMemo(
    () => ({
      data,
      loading,
      error,
    }),
    [data, loading, error]
  );
}
