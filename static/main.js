var keywordsResult = new Vue({
  el: '#keywords-result',
  data: {
    keywords: [],
    show: false
  },
  methods: {
    supply: function(d) {
      this.keywords = d;
    },
    appear: function() { this.show = true; },
    hide: function() { this.show = false; }
  }
})

var categoryDropdown = new Vue({
  el: '#category-dropdown',
  data: {
    selected: ''
  },
  methods: {
    submit: function() {
      keywordsResult.hide();
      axios.post('/start', {'category': this.selected})
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
            setTimeout(this.pollResult, 30000, jobID); // modify to give up after a while
          } else if (status === '200') {
            console.log(data, status);
            keywordsResult.supply(data);
            keywordsResult.appear();
          }
        }
      ).catch( error => { console.log(error); })
    }
  }
})
