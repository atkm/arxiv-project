var keywordsResult = new Vue({
  el: '#keywords-result',
  data: {
    keywords: [],
    show: false,
    loading: false
  },
  methods: {
    supply: function(d) {
      this.keywords = d;
    },
    appear: function() { this.show = true; },
    hide: function() { this.show = false; },
    beginLoading: function() { this.loading = true; },
    doneLoading: function() { this.loading = false; }
  }
})

var categoryDropdown = new Vue({
  el: '#category-dropdown',
  data: {
    selected: '',
    specificity: '2'
  },
  methods: {
    submit: function() {
      keywordsResult.hide();
      keywordsResult.beginLoading();
      axios.post('/start', {'category': this.selected, 'specificity': this.specificity})
      .then(
        response => {
          this.pollResult(response.data);
        } 
      )
      .catch(error => { console.log(error); });
    },

    pollResult: function(jobID) {
      axios.get('/results/' + jobID)
      .then(
        response => {
          status = response.status;
          data = response.data;
          if (status === '202') {
            console.log(data, status);
            setTimeout(this.pollResult, 5000, jobID); // modify to give up after a while
          } else if (status === '200') {
            console.log(data, status);
            keywordsResult.supply(data);
            keywordsResult.doneLoading();
            keywordsResult.appear();
          }
        }
      ).catch( error => {
        keywordsResult.doneLoading();
        console.log(error);
      })
    }
  }
})
