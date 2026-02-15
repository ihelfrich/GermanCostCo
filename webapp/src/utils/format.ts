export const formatNumber = (value: number, digits = 0): string =>
  Number(value || 0).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });

export const formatPct = (value: number, digits = 1): string =>
  `${(Number(value || 0) * 100).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  })}%`;

export const formatEur = (value: number, digits = 0): string =>
  `EUR ${Number(value || 0).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  })}`;
