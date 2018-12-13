import Vue from 'vue';
import { format as formatDate, parse as parseDate } from 'date-fns';

Vue.filter('date', (dateString: string, format: string = 'MMM dd, YYYY') => {
  let date = parseDate(dateString);
  return formatDate(date, format);
});

Vue.filter('lowercase', (str: string) => {
  return str.toLowerCase();
});

Vue.filter(
  'pluralize',
  (noun: string, count: number, substitutions = {}, pluralSuffix = 's') => {
    return (
      `${substitutions[count] || count} ` +
      (count !== 1 ? `${noun}${pluralSuffix}` : noun)
    );
  }
);

Vue.filter('round', function(value, decimals) {
  return (
    Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)
  ).toFixed(decimals);
});

Vue.filter(
  'variablePrecisionNumber',
  (value, minPrecision, maxPrecision) =>
    `TODO: ${value}, ${minPrecision}, ${maxPrecision}`
);
