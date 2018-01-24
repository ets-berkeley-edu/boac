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
          regex = RegExp('\\b' + words[0], 'gi');
        } else {
          var p = '';
          _.each(words, function(word) {
            if (word) {
              p = p.concat('\\b(' + word + ').* ');
            }
          });
          regex = RegExp(_.trimEnd(p), 'gi');
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
