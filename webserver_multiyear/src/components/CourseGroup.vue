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

    <b-row>
      <b-col cols="4" :key="item.Code" v-for="item in sortedCourses">
        <Course :data="item" :choices="choices[item.Code]" />
      </b-col>
    </b-row>
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
  computed: {
    sortedCourses: function () {
      function compare (a, b) {
        if (a.Code < b.Code) {
          return 1
        } else if (a.Code > b.Code) {
          return -1
        }
        return 0
      }

      return [...this.courses].sort(compare)
    }
  },
  props: ['title', 'choices'],
  watch: {
    codesSearch: _.debounce(function (addr) { this.getQuery(addr) }, 500),
    selectCodes: function (code) {
      this.$refs.search_typeahead.inputValue = ''
      this.courses.push(code)
      this.$parent.reload()
    }
  },
  methods: {
    async getQuery (query) {
      const res = await fetch(API_URL.replace(':query', query))
      const suggestions = await res.json()
      this.searchCodes = suggestions
    },
    async addCode (codeId) {
      const res = await fetch(`/api/course/${codeId}`)
      const info = await res.json()
      this.courses.push(info)
      this.$parent.reload()
    },
    remove: function (codeId) {
      this.courses = this.courses.filter((el) => el.Code !== codeId)
      this.$parent.reload()
    },
    reverseReqMap: function (codeId) {
      return this.$parent.reverseReqMap(codeId)
    },
    swap: function (codeId) {
      const found = this.courses.find((el) => el.Code === codeId)
      this.$parent.$refs.taken.courses.push(found)
      this.$parent.$refs.future.courses.push(found)
      this.courses = this.courses.filter((el) => el.Code !== codeId)
      this.$parent.reload()
    },
    getCodes: function () {
      return this.courses.map(el => el.Code)
    },
    updateCodes: async function (newCodes) {
      const newInfo = await Promise.all(newCodes.map(async (el) => {
        const res = await fetch(`/api/course/${el}`)
        return res.json()
      }))

      this.courses = newInfo
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
