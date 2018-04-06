/**
 * Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

(function(angular) {

  'use strict';

  angular.module('boac').service('utilService', function(
    config,
    $anchorScroll,
    $base64,
    $location,
    $rootScope,
    $timeout
  ) {

    var anchorScroll = function(anchorId) {
      $timeout(function() {
        // Clean up location URI
        $location.search('a', null).replace();
        $anchorScroll.yOffset = 50;
        $anchorScroll(anchorId);
      });
    };

    var toBoolOrNull = function(str) {
      return _.isNil(str) ? null : _.lowerCase(str) === 'true';
    };

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
          option.id = option.id || _.toLower(option.name.replace(/\W+/g, '-'));
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

    /**
     * @param  {String}     str      Word/phrase with camelCase
     * @return {String}              All 'camelCase' are converted to 'camel-case'
     */
    var camelCaseToDashes = function(str) {
      return str.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
    };

    /**
     * @param  {String}     str      Word, phrase or whatever
     * @return {String}              Unrecognizable representation of str
     */
    var obfuscate = function(str) {
      var words = _.map(str.split(' '), function(word) {
        var length = word.length;
        if (length <= 1) {
          // A dash or similar
          return word;
        } else if (/\d+/.test(word)) {
          // A number
          return Math.floor(Math.random() * 100000000);
        }
        // Random word
        var chars = _.map(_.range(length), function() {
          return 'abcdefghijklmnopqrstuvwxyz'.charAt(_.random(0, 26));
        });
        return _.capitalize(chars.join(''));
      });
      return words.join(' ');
    };

    var parseError = function(error) {
      $rootScope.pageTitle = 'Error';
      var message = error.message || _.get(error, 'data.message') || error || 'An unexpected server error occurred.';
      return {
        status: error.status || 500,
        message: _.truncate(message, {length: 200})
      };
    };

    var unpackReturnUrl = function(anchorId) {
      var disableBreadcrumb = true;
      if (disableBreadcrumb) {
        // TODO: Cook up a sensible breadcrumb strategy (see BOAC-596) or remove the feature.
        return null;
      }
      var encodedReturnUrl = $location.search().r;
      var url = null;
      if (!_.isEmpty(encodedReturnUrl)) {
        // Parse referring URL
        $location.search('r', null).replace();
        url = $base64.decode(decodeURIComponent(encodedReturnUrl));
        if (anchorId) {
          var anchorParam = 'a=' + anchorId;
          var urlComponents = url.split('?');
          if (urlComponents.length > 1) {
            url = urlComponents.shift();
            var query = urlComponents.join('?');
            query = query.replace(/&?casLogin=true/, '');
            if (query.length) {
              anchorParam = query + '&' + anchorParam;
            }
          }
          url = url + '?' + anchorParam;
        }
      }
      return url;
    };

    var constructReturnToLabel = function(returnUrl) {
      var label = null;
      if (returnUrl) {
        var name = $location.search().referringPageName;
        if (name && !config.demoMode) {
          label = 'Return to ' + name;
          $location.search('referringPageName', null).replace();
        } else if (returnUrl.includes('student')) {
          label = 'Return to student';
        } else {
          label = returnUrl.includes('cohort') ? 'Return to cohort' : 'Return to course';
        }
      }
      return label;
    };

    var getEncodedAbsUrl = function() {
      return encodeURIComponent($base64.encode($location.absUrl()));
    };

    /**
     * @param  {String}     path                    URI of destination
     * @param  {String}     currentPageName         Used to construct 'Return to...' label (see returnUrl above)
     * @return {void}
     */
    var goTo = function(path, currentPageName) {
      var encodedAbsUrl = getEncodedAbsUrl();
      $location.path(path).search({
        r: encodedAbsUrl,
        referringPageName: currentPageName
      });
    };

    var extendSortableNames = function(students) {
      return _.map(students, function(student) {
        return _.extend(student, {
          sortableName: student.lastName + ', ' + student.firstName
        });
      });
    };

    return {
      anchorScroll: anchorScroll,
      camelCaseToDashes: camelCaseToDashes,
      constructReturnToLabel: constructReturnToLabel,
      extendSortableNames: extendSortableNames,
      decorateOptions: decorateOptions,
      format: format,
      getEncodedAbsUrl: getEncodedAbsUrl,
      goTo: goTo,
      unpackReturnUrl: unpackReturnUrl,
      getValuesSelected: getValuesSelected,
      obfuscate: obfuscate,
      parseError: parseError,
      toBoolOrNull: toBoolOrNull
    };
  });

}(window.angular));
