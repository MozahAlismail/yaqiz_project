import React from 'react';
import { Card, MapPreview } from '../../shared/components';
import { Location } from '../../shared/types';
import { texts } from '../../i18n/texts';

interface LocationPanelProps {
  location: Location;
  onOpenMap?: () => void;
}

export const LocationPanel: React.FC<LocationPanelProps> = ({
  location,
  onOpenMap,
}) => {
  return (
    <Card title={texts.acceptedIncident.locationDetails}>
      <MapPreview
        address={location.address}
        mapUrl={location.mapUrl}
        onOpenMap={onOpenMap}
        buttonLabel={texts.actions.viewOnMap}
      />
    </Card>
  );
};

export default LocationPanel;
