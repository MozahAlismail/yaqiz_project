import React from 'react';
import { Input, Button } from '../../shared/components';
import { IconSearch, IconFilter } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface SearchHeaderProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onFilterToggle: () => void;
  showFilterButton?: boolean;
}

export const SearchHeader: React.FC<SearchHeaderProps> = ({
  searchQuery,
  onSearchChange,
  onFilterToggle,
  showFilterButton = true,
}) => {
  return (
    <div className="flex items-center gap-3 bg-white rounded-lg border border-gray-200 p-3">
      <Input
        value={searchQuery}
        onChange={onSearchChange}
        placeholder={texts.placeholders.searchIncidents}
        icon={<IconSearch size={18} />}
        iconPosition="right"
        className="flex-1"
      />
      {showFilterButton && (
        <Button
          variant="outline"
          size="md"
          icon={<IconFilter size={18} />}
          onClick={onFilterToggle}
          ariaLabel={texts.common.filter}
        >
          <span className="hidden sm:inline">{texts.common.filter}</span>
        </Button>
      )}
    </div>
  );
};

export default SearchHeader;
