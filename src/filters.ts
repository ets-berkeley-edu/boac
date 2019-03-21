import numFormat from 'vue-filter-number-format';

export default {
  ceil: value => Math.ceil(value),
  lowercase: (str: string) => {
    return str.toLowerCase();
  },
  numFormat,
  pluralize: (
    noun: string,
    count: number,
    substitutions = {},
    pluralSuffix = 's'
  ) => {
    return (
      `${substitutions[count] || substitutions['other'] || count} ` +
      (count !== 1 ? `${noun}${pluralSuffix}` : noun)
    );
  },
  round: (value, decimals) => {
    return (
      Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)
    ).toFixed(decimals);
  }
};
