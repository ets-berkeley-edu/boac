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

var csso = require('gulp-csso');
var del = require('del');
var gulp = require('gulp');
var filter = require('gulp-filter');
var rev = require('gulp-rev');
var revReplace = require('gulp-rev-replace');

gulp.task('clean', function(done) {
  return del([ 'dist' ], done);
});

gulp.task('rev', function(done) {
  // No rev() for third-party js/css files
  gulp.src('boac/static/lib/**/*').pipe(gulp.dest('dist/static/lib'));
  var css = filter('boac/static/app/**/*.css', {restore: true});
  // The index.html filename, unlike js/css files, is preserved
  var index = filter(['**/*', '!**/favicon.ico', '!**/index.html'], {restore: true});
  // We cannot minify our js due to http://budiirawan.com/uglify-angular-error-unpr-unknown-provider-aprovider/
  gulp.src(['boac/static/**', 'boac/templates/index.html'])
    .pipe(css)
    .pipe(csso())
    .pipe(css.restore)
    .pipe(index)
    .pipe(rev())
    .pipe(index.restore)
    .pipe(revReplace())
    .pipe(gulp.dest('dist/static'))
    .on('end', function() {
      // Move index.html to location consistent with source dir structure
      var indexHtml = 'dist/static/index.html';
      gulp.src(indexHtml)
        .pipe(gulp.dest('dist/templates'))
        .on('end', function() {
          return del(indexHtml);
        });
    });
  return done();
});

gulp.task('dist', gulp.series('clean', 'rev'));
