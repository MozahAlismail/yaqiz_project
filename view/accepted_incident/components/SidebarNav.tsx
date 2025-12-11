import React from 'react';
import { Card, ListItem } from '../../shared/components';
import { IconDocument } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface RecentReport {
  id: string;
  label: string;
}

interface SidebarNavProps {
  recentReports: RecentReport[];
  onReportClick: (id: string) => void;
  onNavigateToDashboard?: () => void;
}

export const SidebarNav: React.FC<SidebarNavProps> = ({
  recentReports,
  onReportClick,
  onNavigateToDashboard,
}) => {
  return (
    <aside className="space-y-4">
      <Card>
        <div className="text-center py-2">
          <button
            type="button"
            onClick={onNavigateToDashboard}
            className="text-lg font-bold text-[#0b5ac1] hover:underline"
          >
            {texts.navigation.alertsSystem}
          </button>
        </div>
      </Card>

      <Card title={texts.navigation.recentReports}>
        <nav aria-label={texts.navigation.recentReports}>
          <ul className="space-y-1">
            {recentReports.map((report) => (
              <li key={report.id}>
                <ListItem
                  onClick={() => onReportClick(report.id)}
                  icon={<IconDocument size={16} />}
                >
                  <span className="text-sm font-medium text-gray-700">
                    #{report.label}
                  </span>
                </ListItem>
              </li>
            ))}
          </ul>
        </nav>
      </Card>
    </aside>
  );
};

export default SidebarNav;
