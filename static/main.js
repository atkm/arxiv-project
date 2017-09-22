var arxiv = new Vue({
  el: '#atom-response',
  data: {
    message: {},
  },
  mounted: function() {
    axios.get('/arxiv').then(
      response => { this.message = response; }
    )
  },
  computed: {
    computedMessage: function() {
      return this.message;
    }
  }
})
