/**
 * Text and number formatting utilities
 */

/**
 * Format phone number for display
 * Handles Saudi Arabian phone numbers
 * @param phone Phone number string
 */
export function formatPhoneNumber(phone: string): string {
  if (!phone) return '';

  // Remove all non-digit characters
  const digits = phone.replace(/\D/g, '');

  // Handle Saudi format: +966 5X XXX XXXX
  if (digits.length === 12 && digits.startsWith('966')) {
    return `+${digits.slice(0, 3)} ${digits.slice(3, 5)} ${digits.slice(5, 8)} ${digits.slice(8)}`;
  }

  // Handle local Saudi format: 05X XXX XXXX
  if (digits.length === 10 && digits.startsWith('05')) {
    return `${digits.slice(0, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}`;
  }

  // Handle 9-digit format (without leading 0): 5X XXX XXXX
  if (digits.length === 9 && digits.startsWith('5')) {
    return `0${digits.slice(0, 2)} ${digits.slice(2, 5)} ${digits.slice(5)}`;
  }

  // Return as-is for other formats
  return phone;
}

/**
 * Truncate text to a maximum length with ellipsis
 * @param text Text to truncate
 * @param maxLength Maximum length (default: 100)
 * @param ellipsis Ellipsis string (default: '...')
 */
export function truncateText(
  text: string,
  maxLength: number = 100,
  ellipsis: string = '...'
): string {
  if (!text || text.length <= maxLength) {
    return text || '';
  }

  // Find the last space before maxLength to avoid cutting words
  const lastSpace = text.lastIndexOf(' ', maxLength - ellipsis.length);
  const cutoff = lastSpace > 0 ? lastSpace : maxLength - ellipsis.length;

  return text.slice(0, cutoff).trim() + ellipsis;
}

/**
 * Format a number with Arabic-Indic numerals
 * @param num Number to format
 */
export function toArabicNumerals(num: number | string): string {
  const arabicNumerals = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
  return String(num).replace(/[0-9]/g, (d) => arabicNumerals[parseInt(d)] || d);
}

/**
 * Format a number with thousands separators
 * @param num Number to format
 * @param locale Locale code (default: 'ar-SA')
 */
export function formatNumber(num: number, locale: string = 'ar-SA'): string {
  return new Intl.NumberFormat(locale).format(num);
}

/**
 * Format a percentage
 * @param value Decimal value (0-1) or percentage (0-100)
 * @param decimals Number of decimal places (default: 0)
 * @param isDecimal Whether the value is a decimal (default: true)
 */
export function formatPercentage(
  value: number,
  decimals: number = 0,
  isDecimal: boolean = true
): string {
  const percentage = isDecimal ? value * 100 : value;
  return `${percentage.toFixed(decimals)}%`;
}

/**
 * Convert confidence score (0-1) to percentage string
 * @param confidence Confidence score between 0 and 1
 */
export function formatConfidence(confidence: number): string {
  const percentage = Math.round(confidence * 100);
  return `${percentage}%`;
}

/**
 * Capitalize the first letter of a string
 * @param text Text to capitalize
 */
export function capitalize(text: string): string {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/**
 * Convert snake_case to readable text
 * @param text Snake case text
 */
export function snakeToReadable(text: string): string {
  if (!text) return '';
  return text
    .split('_')
    .map((word) => capitalize(word))
    .join(' ');
}

/**
 * Generate initials from a name
 * @param name Full name
 * @param maxInitials Maximum number of initials (default: 2)
 */
export function getInitials(name: string, maxInitials: number = 2): string {
  if (!name) return '';

  const words = name.trim().split(/\s+/);
  const initials = words
    .slice(0, maxInitials)
    .map((word) => word.charAt(0).toUpperCase())
    .join('');

  return initials;
}

/**
 * Sanitize text for safe display (basic XSS prevention)
 * @param text Text to sanitize
 */
export function sanitizeText(text: string): string {
  if (!text) return '';

  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };

  return text.replace(/[&<>"']/g, (char) => map[char] || char);
}

export const formatUtils = {
  formatPhoneNumber,
  truncateText,
  toArabicNumerals,
  formatNumber,
  formatPercentage,
  formatConfidence,
  capitalize,
  snakeToReadable,
  getInitials,
  sanitizeText,
};

export default formatUtils;
