import React from 'react';
import { Card, Button, FilterChips, RadioGroup, Select } from '../../shared/components';
import { QuickFilter, SelectOption } from '../../shared/types';
import { texts } from '../../i18n/texts';

interface FilterPanelProps {
  quickFilters: QuickFilter[];
  selectedQuickFilter: string;
  severityOptions: SelectOption[];
  selectedSeverity: string;
  incidentTypeOptions: SelectOption[];
  selectedIncidentType: string;
  authorityOptions: SelectOption[];
  selectedAuthority: string;
  monthOptions: SelectOption[];
  selectedMonth: string;
  yearOptions: SelectOption[];
  selectedYear: string;
  onQuickFilterChange: (id: string) => void;
  onSeverityChange: (value: string) => void;
  onIncidentTypeChange: (value: string) => void;
  onAuthorityChange: (value: string) => void;
  onMonthChange: (value: string) => void;
  onYearChange: (value: string) => void;
  onApply: () => void;
  onCancel: () => void;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  quickFilters,
  selectedQuickFilter,
  severityOptions,
  selectedSeverity,
  incidentTypeOptions,
  selectedIncidentType,
  authorityOptions,
  selectedAuthority,
  monthOptions,
  selectedMonth,
  yearOptions,
  selectedYear,
  onQuickFilterChange,
  onSeverityChange,
  onIncidentTypeChange,
  onAuthorityChange,
  onMonthChange,
  onYearChange,
  onApply,
  onCancel,
}) => {
  return (
    <Card title={texts.incidentsList.filterReports} className="h-full">
      <div className="space-y-6">
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">
            {texts.incidentsList.quickFilters}
          </h4>
          <FilterChips
            filters={quickFilters}
            selectedId={selectedQuickFilter}
            onChange={onQuickFilterChange}
          />
        </div>

        <div>
          <RadioGroup
            name="severity"
            value={selectedSeverity}
            onChange={onSeverityChange}
            options={severityOptions}
            label={texts.incidentsList.severityFilter}
          />
        </div>

        <Select
          value={selectedIncidentType}
          onChange={onIncidentTypeChange}
          options={incidentTypeOptions}
          label={texts.incidentsList.incidentTypeFilter}
          placeholder={texts.placeholders.selectIncidentType}
        />

        <Select
          value={selectedAuthority}
          onChange={onAuthorityChange}
          options={authorityOptions}
          label={texts.incidentsList.authorityFilter}
          placeholder={texts.placeholders.selectAuthority}
        />

        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">
            {texts.incidentsList.dateFilter}
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <Select
              value={selectedMonth}
              onChange={onMonthChange}
              options={monthOptions}
              placeholder={texts.placeholders.selectMonth}
            />
            <Select
              value={selectedYear}
              onChange={onYearChange}
              options={yearOptions}
              placeholder={texts.placeholders.selectYear}
            />
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <Button variant="primary" fullWidth onClick={onApply}>
            {texts.common.apply}
          </Button>
          <Button variant="ghost" fullWidth onClick={onCancel}>
            {texts.common.cancel}
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default FilterPanel;
