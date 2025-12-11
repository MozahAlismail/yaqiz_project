import React from 'react';
import { Card, Select, SeveritySelector, ProgressBar } from '../../shared/components';
import { SeverityLevel, SelectOption } from '../../shared/types';
import { texts } from '../../i18n/texts';

interface AnalysisPanelProps {
  reportType: string;
  severity: SeverityLevel | '';
  responsibleAuthority: string;
  confidence: number;
  reportTypeOptions: SelectOption[];
  authorityOptions: SelectOption[];
  onReportTypeChange: (value: string) => void;
  onSeverityChange: (value: SeverityLevel) => void;
  onAuthorityChange: (value: string) => void;
}

const severityOptions: { value: SeverityLevel; label: string }[] = [
  { value: 'high', label: texts.severity.high },
  { value: 'medium', label: texts.severity.medium },
  { value: 'low', label: texts.severity.low },
];

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({
  reportType,
  severity,
  responsibleAuthority,
  confidence,
  reportTypeOptions,
  authorityOptions,
  onReportTypeChange,
  onSeverityChange,
  onAuthorityChange,
}) => {
  return (
    <Card title={texts.realtime.systemAnalysis}>
      <div className="space-y-4">
        <Select
          value={reportType}
          onChange={onReportTypeChange}
          options={reportTypeOptions}
          label={texts.incident.reportType}
          placeholder={texts.placeholders.selectIncidentType}
        />

        <SeveritySelector
          value={severity}
          onChange={onSeverityChange}
          options={severityOptions}
          label={texts.incident.severity}
        />

        <Select
          value={responsibleAuthority}
          onChange={onAuthorityChange}
          options={authorityOptions}
          label={texts.incident.responsibleAuthority}
          placeholder={texts.placeholders.selectAuthority}
        />

        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              {texts.realtime.confidence}
            </span>
            <span className="text-lg font-bold text-[#02a63e]">{confidence}%</span>
          </div>
          <ProgressBar
            value={confidence}
            segments={10}
            variant="success"
            size="md"
          />
        </div>
      </div>
    </Card>
  );
};

export default AnalysisPanel;
