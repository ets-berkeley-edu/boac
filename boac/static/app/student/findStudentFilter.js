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

  angular.module('boac').filter('findStudentFilter', function() {

    return function(options, input) {
      var filtered = [];
      var phrase = _.trim(input);
      if (phrase) {
        var words = _.split(phrase, ' ');
        var regex;
        if (words.length === 1) {
          regex = RegExp('\\b' + words[0], 'i');
        } else {
          var p = '';
          _.each(words, function(word) {
            if (word) {
              p = p.concat('\\b(' + word + ').* ');
            }
          });
          regex = RegExp(_.trimEnd(p), 'i');
        }
        _.each(options, function(option) {
          if (regex.test(option.name)) {
            filtered.push(option);
          }
        });
      } else {
        filtered = options;
      }
      return filtered;
    };

  }).filter('boldNamesFilter', function($sce) {

    return function(label, query) {
      var html = label;
      var words = _.split(_.trim(query), ' ');
      if (words.length) {
        _.each(words, function(word) {
          var regex = RegExp('(.*)(\\b' + word + ')(.*)', 'i');
          html = html.replace(regex, '$1<strong>$2</strong>$3');
        });
      }
      return $sce.trustAsHtml(html);
    };

  });

}(window.angular));
