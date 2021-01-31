<template>
  <div class="body">
    <b-row>
      <b-col cols="9">
        <b-table responsive fixed :items="items" :fields="fields">
          <template #table-colgroup="scope">
            <col
              v-for="field in scope.fields"
              :key="field.key"
              :style="{ width: '140px' }"
            >
          </template>

          <template #cell()="data">
            <CourseSmall v-for="item in data['value']" :key="item" :code="item" />
          </template>
        </b-table>
      </b-col>
      <b-col cols="3">
        <CourseGroup ref="future" title="Future Courses" :choices="choicesNeeded"/>
        <CourseGroup ref="taken" style="padding-top:60px" title="Taken Courses" :choices="choicesNeeded"/>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import CourseSmall from '@/components/CourseSmall.vue'
import CourseGroup from '@/components/CourseGroup.vue'

const tempData = { F21: ['CIS*1300', 'CIS*1910', 'ECON*1050', 'ECON*1100', 'STAT*2040', 'ACCT*2220'], W22: ['CIS*2500', 'ECON*2770', 'ACCT*3330'], S22: ['ACCT*3340'], F22: ['CIS*2430', 'CIS*2520', 'ECON*3740', 'ACCT*4220'], W23: ['CIS*2750'], S23: [], F23: ['CIS*3750', 'ECON*4640'], W24: [], S24: [], F24: ['CIS*4150'] }

export default {
  mounted () {
    this.parseData(tempData)
    this.getChoices()
  },
  methods: {
    parseData: function (input) {
      this.items = [input]
      this.fields = Object.keys(input)
    },
    getChoices: async function () {
      const res = await fetch('/api/generate')
      const choices = await res.json()
      this.choicesNeeded = choices
    },
    reload: async function () {
      const coursesTaken = this.$refs.taken.getCodes()
      const coursesFuture = this.$refs.future.getCodes()

      const res = await fetch('/api/generate', {
        method: 'POST',
        body: JSON.stringify({ taken: coursesTaken, future: coursesFuture }),
        headers: { 'Content-Type': 'application/json' }
      })

      const choices = await res.json()
      this.choicesNeeded = choices[1]
      this.$refs.future.updateCodes(choices[0])
      this.parseData(choices[2])
      console.log(choices[1])
    }
  },
  data () {
    return {
      fields: [],
      items: [],
      choicesNeeded: { }
    }
  },
  components: {
    CourseSmall,
    CourseGroup
  },
  name: 'Home'
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.body {
  margin-left: 10%;
  margin-right: 10%;
  margin-top: 2%;
  min-height: 100%;
}
</style>
