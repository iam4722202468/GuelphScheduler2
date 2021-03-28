<template>
  <div>
    <div class="courseBox" :style="dynamicStyle">
      <b-row style="padding-left:15px; padding-top:10px">
        <b-col cols="9">
          <b>{{data.Code}}</b><br>
          {{data.Name}}<br>
          {{data.Num_Credits}}<br>
          <br>
          <div v-if="reverseReqMap().length > 0">Required By</div>
          <b-row>
            <b-col cols="6" :key="codeId" v-for="codeId in reverseReqMap()">
              <CourseMini :code="codeId"/>
            </b-col>
          </b-row>
        </b-col>
        <b-col cols="2">
          <b-row>
            <b-col v-on:click="remove" class="hoverButton btn btn-outline-danger" title="Delete">
              <b-icon icon="trash"></b-icon>
            </b-col>
            <b-col v-on:click="swap" class="hoverButton btn btn-outline-primary" title="Swap Group">
              <b-icon icon="arrow-left-right"></b-icon>
            </b-col>
          </b-row>
        </b-col>
      </b-row>
      <hr v-if="choices && choices.lenth > 0">
      <Choice v-if="choices" :data="choices" :parent="this"/>
    </div>
  </div>
</template>

<script>
import Choice from '@/components/Choice.vue'
import CourseMini from '@/components/CourseMini.vue'

export default {
  name: 'Course',
  props: ['data', 'choices'],
  methods: {
    addCode: function (codeId) {
      this.$parent.addCode(codeId)
    },
    remove: function () {
      this.$parent.remove(this.data.Code)
    },
    swap: function () {
      this.$parent.swap(this.data.Code)
    },
    reverseReqMap: function () {
      return this.$parent.reverseReqMap(this.data.Code)
    },

    lightenColor: function (color, percent) {
      const num = parseInt(color, 16)
      const amt = Math.round(2.55 * percent)
      const R = (num >> 16) + amt
      const B = (num >> 8 & 0x00FF) + amt
      const G = (num & 0x0000FF) + amt
      return (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (B < 255 ? B < 1 ? 0 : B : 255) * 0x100 + (G < 255 ? G < 1 ? 0 : G : 255)).toString(16).slice(1)
    },

    hashCode: function (str) {
      var hash = 0
      for (var i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash)
      }
      return hash
    },
    intToRGB: function (i) {
      var c = (i & 0x00FFFFFF)
        .toString(16)
        .toUpperCase()

      return '00000'.substring(0, 6 - c.length) + c
    }
  },
  computed: {
    dynamicStyle () {
      return {
        // in the case of redComp, greenComp and blueComp are a vue prop or data
        'background-color': `#${this.lightenColor(this.intToRGB(this.hashCode(this.data.Code)), 60)}`,
        border: `solid 2px #${this.intToRGB(this.hashCode(this.data.Code))}`
      }
    }
  },
  components: {
    Choice,
    CourseMini
  }
}
</script>

<style scoped lang="scss">
.courseBox {
  margin-right: -4px;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-radius: 10px;
  max-width: 300px;
}

.hoverButton
{
  margin-top: 1em;
  border-radius: 60px;
  padding-left: 0.66em;
}
</style>
