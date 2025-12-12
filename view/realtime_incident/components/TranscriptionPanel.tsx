import React from 'react';
import { Card, HighlightedText, TextSegment } from '../../shared/components';
import { texts } from '../../i18n/texts';

interface TranscriptionData {
  original_text: string;
  original_language: string;
  translated_text: string | null;
  translated_language: string | null;
  translation_enabled: boolean;
}

interface TranscriptionPanelProps {
  segments: TextSegment[];
  /** New transcription data with both original and translated */
  transcriptionData?: TranscriptionData | null;
  /** Whether translation is enabled */
  isTranslationEnabled?: boolean;
  onEditText?: () => void;
}

const languageNames: Record<string, string> = {
  ar: 'العربية',
  en: 'English',
  es: 'Español',
  fr: 'Français',
  de: 'Deutsch',
  unknown: 'غير معروف',
};

export const TranscriptionPanel: React.FC<TranscriptionPanelProps> = ({
  segments,
  transcriptionData,
  isTranslationEnabled = false,
  onEditText,
}) => {
  // If we have transcription data, show both original and translated
  const hasTranscriptionData = transcriptionData && transcriptionData.original_text;

  return (
    <Card
      title={texts.realtime.convertedText}
      headerAction={
        onEditText && (
          <button
            type="button"
            onClick={onEditText}
            className="text-sm text-[#0b5ac1] hover:underline"
          >
            {texts.acceptedIncident.editText}
          </button>
        )
      }
      className="h-full"
    >
      {hasTranscriptionData ? (
        <div className="space-y-4">
          {/* Original Text Section */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">
                النص الأصلي
              </span>
              <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                {languageNames[transcriptionData.original_language] || transcriptionData.original_language}
              </span>
            </div>
            <p className="text-gray-900 leading-relaxed">
              {transcriptionData.original_text}
            </p>
          </div>

          {/* Translated Text Section - Only show if translation is enabled */}
          {isTranslationEnabled && (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-700">
                  النص المترجم
                </span>
                {transcriptionData.translated_language && (
                  <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">
                    {languageNames[transcriptionData.translated_language] || transcriptionData.translated_language}
                  </span>
                )}
              </div>
              {transcriptionData.translated_text ? (
                <p className="text-gray-900 leading-relaxed">
                  {transcriptionData.translated_text}
                </p>
              ) : (
                <p className="text-gray-400 italic">
                  جاري الترجمة...
                </p>
              )}
            </div>
          )}
        </div>
      ) : (
        /* Fallback to segments display */
        <div className="bg-gray-50 rounded-lg p-4 min-h-[200px]">
          <HighlightedText segments={segments} />
        </div>
      )}
    </Card>
  );
};

export default TranscriptionPanel;
