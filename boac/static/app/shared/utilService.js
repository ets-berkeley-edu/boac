(function(angular) {

  'use strict';

  angular.module('boac').service('utilService', function() {

    var format = function(str, tokens) {
      var formatted = str;
      _.each(tokens, function(value, key) {
        formatted = formatted.replace('${' + key + '}', value);
      });
      return formatted;
    };

    /**
     * Standard set of menu options per expectations of cohort-view, etc.
     *
     * @param  {Array}    options      Set of menu options
     * @param  {String}   pkRef        Key used to get primary-key of each option in options
     * @return {Array}                 Enhanced set of menu options (eg, unique 'id' property per option)
     */
    var decorateOptions = function(options, pkRef) {
      return _.map(options, function(option) {
        if (option && option[pkRef]) {
          option.name = option.name || option[pkRef];
          option.value = option.value || option[pkRef];
          option.id = option.id || _.toLower(option.value.replace(/\W+/g, '-'));
        }
        return option;
      });
    };

    /**
     * Extract 'value' property of each selected option in options array.
     *
     * @param  {Array}    options      Set of menu options
     * @param  {String}   [valueRef]   Optional key used to lookup value of menu option. Default key is 'value'.
     * @return {Array}                 Values (strings) of selected options
     */
    var getValuesSelected = function(options, valueRef) {
      return _.map(_.filter(options, 'selected'), valueRef || 'value');
    };

    return {
      decorateOptions: decorateOptions,
      format: format,
      getValuesSelected: getValuesSelected
    };
  });

}(window.angular));
