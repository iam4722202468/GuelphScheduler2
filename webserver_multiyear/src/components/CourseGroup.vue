<template>
  <div class="courseGroup">
    <h3> {{ title }} </h3>
    <hr>
    <vue-bootstrap-typeahead
      :data="searchCodes"
      v-model="codesSearch"
      :minMatchingChars="0"
      :serializer="s => s.Code + ' - ' + s.Name + ' [' + s.Num_Credits + ']'"
      placeholder="Search"
      @hit="selectCodes = $event"
      ref="search_typeahead"
      style="padding-bottom: 10px"
    ></vue-bootstrap-typeahead>

    <Course v-for="item in courses" :key="item.Code" :data="item" :choices="choices[item.Code]" />
  </div>
</template>

<script>
import Course from '@/components/Course.vue'
import _ from 'underscore'

const API_URL = '/api/query/:query'

export default {
  name: 'CourseGroup',
  data () {
    return {
      courses: [],
      searchCodes: [],
      codesSearch: '',
      selectCodes: null
    }
  },
  props: ['title', 'choices'],
  watch: {
    codesSearch: _.debounce(function (addr) { this.getAddresses(addr) }, 500),
    selectCodes: function (code) {
      this.$refs.search_typeahead.inputValue = ''
      this.courses.push(code)
    }
  },
  methods: {
    async getAddresses (query) {
      const res = await fetch(API_URL.replace(':query', query))
      const suggestions = await res.json()
      this.searchCodes = suggestions
    }
  },
  components: {
    Course
  }
}
</script>

<style scoped lang="scss">
.courseGroup {
}

hr {
  margin-top: 1rem;
  margin-bottom: 1rem;
  border: 0;
  border-top-color: currentcolor;
  border-top-style: none;
  border-top-width: 0px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}
</style>
