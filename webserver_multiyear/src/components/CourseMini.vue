<template>
  <div class="courseBox">
      <div
          class="courseBox"
          :style="dynamicStyle"
      >
            <b>{{code}}</b>
      </div>
  </div>
</template>

<script>

export default {
  name: 'CourseMini',
  props: ['code'],
  methods: {
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
      const color = this.intToRGB(this.hashCode(this.code))

      return {
        // in the case of redComp, greenComp and blueComp are a vue prop or data
        'background-color': `#${this.lightenColor(color, 60)}`,
        border: `solid 2px #${color}`
      }
    }
  }
}
</script>

<style scoped lang="scss">
.courseBox {
  padding-top: 1px;
  text-align: center;
  width: 70px;
  font-size: 0.85em;
}
</style>
