/**
 * Date formatting utilities with Arabic locale support
 */

/**
 * Format a date to a localized date string
 * @param date Date string, timestamp, or Date object
 * @param locale Locale code (default: 'ar-SA')
 */
export function formatDate(
  date: string | number | Date,
  locale: string = 'ar-SA'
): string {
  const dateObj = new Date(date);

  if (isNaN(dateObj.getTime())) {
    return '';
  }

  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(dateObj);
}

/**
 * Format a date to a localized time string
 * @param date Date string, timestamp, or Date object
 * @param locale Locale code (default: 'ar-SA')
 */
export function formatTime(
  date: string | number | Date,
  locale: string = 'ar-SA'
): string {
  const dateObj = new Date(date);

  if (isNaN(dateObj.getTime())) {
    return '';
  }

  return new Intl.DateTimeFormat(locale, {
    hour: '2-digit',
    minute: '2-digit',
  }).format(dateObj);
}

/**
 * Format a date to both date and time
 * @param date Date string, timestamp, or Date object
 * @param locale Locale code (default: 'ar-SA')
 */
export function formatDateTime(
  date: string | number | Date,
  locale: string = 'ar-SA'
): string {
  const dateObj = new Date(date);

  if (isNaN(dateObj.getTime())) {
    return '';
  }

  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(dateObj);
}

/**
 * Format duration in seconds to mm:ss or hh:mm:ss format
 * @param seconds Duration in seconds
 */
export function formatDuration(seconds: number): string {
  if (seconds < 0 || !isFinite(seconds)) {
    return '00:00';
  }

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  const pad = (n: number): string => n.toString().padStart(2, '0');

  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(secs)}`;
  }

  return `${pad(minutes)}:${pad(secs)}`;
}

/**
 * Format duration in seconds to Arabic readable format
 * @param seconds Duration in seconds
 */
export function formatDurationArabic(seconds: number): string {
  if (seconds < 0 || !isFinite(seconds)) {
    return '٠ ثانية';
  }

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  const parts: string[] = [];

  if (hours > 0) {
    parts.push(`${hours} ساعة`);
  }
  if (minutes > 0) {
    parts.push(`${minutes} دقيقة`);
  }
  if (secs > 0 || parts.length === 0) {
    parts.push(`${secs} ثانية`);
  }

  return parts.join(' و ');
}

/**
 * Get relative time string (e.g., "منذ 5 دقائق")
 * @param date Date string, timestamp, or Date object
 * @param locale Locale code (default: 'ar')
 */
export function getRelativeTime(
  date: string | number | Date,
  locale: string = 'ar'
): string {
  const dateObj = new Date(date);

  if (isNaN(dateObj.getTime())) {
    return '';
  }

  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });

  if (diffInSeconds < 60) {
    return rtf.format(-diffInSeconds, 'second');
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return rtf.format(-diffInMinutes, 'minute');
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return rtf.format(-diffInHours, 'hour');
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) {
    return rtf.format(-diffInDays, 'day');
  }

  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return rtf.format(-diffInMonths, 'month');
  }

  const diffInYears = Math.floor(diffInMonths / 12);
  return rtf.format(-diffInYears, 'year');
}

/**
 * Check if a date is today
 * @param date Date string, timestamp, or Date object
 */
export function isToday(date: string | number | Date): boolean {
  const dateObj = new Date(date);
  const today = new Date();

  return (
    dateObj.getDate() === today.getDate() &&
    dateObj.getMonth() === today.getMonth() &&
    dateObj.getFullYear() === today.getFullYear()
  );
}

export const dateUtils = {
  formatDate,
  formatTime,
  formatDateTime,
  formatDuration,
  formatDurationArabic,
  getRelativeTime,
  isToday,
};

export default dateUtils;
