<script>
export default {
  name: 'Berkeley',
  methods: {
    previousSisTermId(termId) {
      var previousTermId = '';
      var strTermId = termId.toString();
      switch (strTermId.slice(3)) {
        case '2':
          previousTermId =
            (parseInt(strTermId.slice(0, 3), 10) - 1).toString() + '8';
          break;
        case '5':
          previousTermId = strTermId.slice(0, 3) + '2';
          break;
        case '8':
          previousTermId = strTermId.slice(0, 3) + '5';
          break;
        default:
          break;
      }
      return previousTermId;
    },
    termNameForSisId(termId) {
      var strTermId = termId.toString();
      var termName = '20' + strTermId.slice(1, 3);
      switch (strTermId.slice(3)) {
        case '2':
          termName = 'Spring ' + termName;
          break;
        case '5':
          termName = 'Summer ' + termName;
          break;
        case '8':
          termName = 'Fall ' + termName;
          break;
        default:
          break;
      }
      return termName;
    }
  }
};
</script>
