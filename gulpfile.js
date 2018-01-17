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
  var index = filter(['**/*', '!**/index.html', '!**/maintenance.html'], {restore: true});
  // We cannot minify our js due to http://budiirawan.com/uglify-angular-error-unpr-unknown-provider-aprovider/
  gulp.src(['boac/static/app/**', 'boac/templates/index.html'])
    .pipe(css)
    .pipe(csso())
    .pipe(css.restore)
    .pipe(index)
    .pipe(rev())
    .pipe(index.restore)
    .pipe(revReplace())
    .pipe(gulp.dest('dist/static/app'))
    .on('end', function() {
      // Move index.html to location consistent with source dir structure
      var indexHtml = 'dist/static/app/index.html';
      gulp.src(indexHtml)
        .pipe(gulp.dest('dist/templates'))
        .on('end', function() {
          return del(indexHtml);
        });
    });
  return done();
});

gulp.task('dist', gulp.series('clean', 'rev'));
