
export default {
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
  }
};
