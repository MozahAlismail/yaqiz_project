import React from 'react';
import { IconMapPin, IconExternalLink } from '../icons';

interface MapPreviewProps {
  address: string;
  imageUrl?: string;
  mapUrl?: string;
  onOpenMap?: () => void;
  buttonLabel?: string;
  className?: string;
}

export const MapPreview: React.FC<MapPreviewProps> = ({
  address,
  imageUrl,
  mapUrl,
  onOpenMap,
  buttonLabel,
  className = '',
}) => {
  return (
    <div className={`rounded-lg overflow-hidden border border-gray-200 ${className}`}>
      <div className="relative h-40 bg-gray-100">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Map location"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <IconMapPin size={48} className="text-gray-300" />
          </div>
        )}
      </div>
      <div className="p-3 bg-white">
        <div className="flex items-start gap-2 mb-3">
          <IconMapPin size={16} className="text-gray-400 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-gray-700 [direction:rtl]">{address}</p>
        </div>
        {(onOpenMap || mapUrl) && (
          <a
            href={mapUrl}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => {
              if (onOpenMap) {
                e.preventDefault();
                onOpenMap();
              }
            }}
            className="flex items-center justify-center gap-2 w-full px-4 py-2 rounded-lg
              bg-[#0b5ac1] text-white text-sm font-medium
              hover:bg-[#0948a3] transition-colors"
          >
            <IconExternalLink size={16} />
            <span>{buttonLabel}</span>
          </a>
        )}
      </div>
    </div>
  );
};

export default MapPreview;
