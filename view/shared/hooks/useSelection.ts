import { useState, useCallback } from 'react';

export const useSelection = <T extends string | number>(
  initialSelection: T[] = []
): {
  selectedIds: T[];
  isSelected: (id: T) => boolean;
  toggle: (id: T) => void;
  select: (id: T) => void;
  deselect: (id: T) => void;
  selectAll: (ids: T[]) => void;
  deselectAll: () => void;
  setSelection: (ids: T[]) => void;
} => {
  const [selectedIds, setSelectedIds] = useState<T[]>(initialSelection);

  const isSelected = useCallback(
    (id: T) => selectedIds.includes(id),
    [selectedIds]
  );

  const toggle = useCallback((id: T) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  }, []);

  const select = useCallback((id: T) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev : [...prev, id]));
  }, []);

  const deselect = useCallback((id: T) => {
    setSelectedIds((prev) => prev.filter((i) => i !== id));
  }, []);

  const selectAll = useCallback((ids: T[]) => {
    setSelectedIds(ids);
  }, []);

  const deselectAll = useCallback(() => {
    setSelectedIds([]);
  }, []);

  const setSelection = useCallback((ids: T[]) => {
    setSelectedIds(ids);
  }, []);

  return {
    selectedIds,
    isSelected,
    toggle,
    select,
    deselect,
    selectAll,
    deselectAll,
    setSelection,
  };
};

export default useSelection;
